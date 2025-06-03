import re
from django.core.cache import cache
from django_redis import get_redis_connection
import django_filters
from rest_framework import filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
)
from django.db.models import Count
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from urllib.parse import urlencode

from core.api_views import BaseGenericViewSet
from core.serializers import (
    BaseSuccessResponseSerializer,
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseNotFoundResponseSerializer,
)
from core.exceptions import CourseException, UserException, EnrollmentException
from core.mixins import FormatDataMixin, CustomListModelMixin
from core.permissions import IsInstructor
from courses.permissions import CoursePermission
from courses.services import CourseServices

from .response_schema import course_response_schema

from ..models import Course, Category
from .serializers import (
    CourseCreateSerializer,
    CourseDataSerializer,
    CourseUpdateSerializer,
    CategoryListSerializer,
    EnrollmentCreateOrEditSerializer,
    TopCoursesSerializer,
    CourseStudentResponseSerializer,
)
from django.conf import settings

User = get_user_model()


class CustomFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(method="filter_status")
    category = django_filters.UUIDFilter(field_name="category__id")

    def filter_status(self, queryset, name, value):
        status_list = value.split(",")
        return queryset.filter(status__in=status_list)

    class Meta:
        model = Course
        fields = ["category"]


@extend_schema_view(
    list=extend_schema(
        description="List all courses with pagination and custom response format.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Course title or description.",
                location=OpenApiParameter.QUERY,
                type=str,
                required=False,
            ),
            OpenApiParameter(
                name="limit",
                description="Maximum number of resources that will be returned.",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="offset",
                description="Number of resources to skip.",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="status",
                description="Filter courses by status.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="category",
                description="Filter courses by category UUID.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="enrolled",
                description="Filter enrolled courses (students only).",
                required=False,
                type=bool,
            ),
        ],
    ),
    create=extend_schema(
        description="Create a course.",
        request=CourseCreateSerializer,
        responses={
            201: course_response_schema,
            400: BaseBadRequestResponseSerializer,
        },
    ),
    retrieve=extend_schema(
        description="Retrieve a single course",
        responses={
            200: course_response_schema,
            404: BaseBadRequestResponseSerializer,
        },
    ),
    partial_update=extend_schema(
        description="Update course.",
        request=CourseUpdateSerializer,
        responses={
            200: course_response_schema,
            400: BaseBadRequestResponseSerializer,
            403: BaseForbiddenResponseSerializer,
        },
    ),
    enroll=extend_schema(
        description="Enroll a student in a course.",
        request=EnrollmentCreateOrEditSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            400: BaseBadRequestResponseSerializer,
            403: BaseForbiddenResponseSerializer,
        },
    ),
    leave=extend_schema(
        description="Leave a course.",
        request=EnrollmentCreateOrEditSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            400: BaseBadRequestResponseSerializer,
            403: BaseForbiddenResponseSerializer,
        },
    ),
)
class CourseViewSet(
    FormatDataMixin,
    BaseGenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
):
    """
    Course view set

    - People who do not need to log in can still see.
    - Students can see the courses they are enrolled in.
    - Can filter courses with category, status, and instructor.

    Filters:
        - category: Filter courses by category.
        - status: Filter courses by status.
        - instructor: Filter courses by enrollment status (students only).

    Returns:
        Response: A paginated list of courses with metadata.
    """

    resource_name = "courses"
    serializer_class = CourseDataSerializer
    queryset = Course.objects.all()
    permission_classes = [CoursePermission]
    http_method_names = ["get", "post", "patch"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CustomFilter
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.action == "get_students":
            return CourseStudentResponseSerializer
        return CourseDataSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned courses to those enrolled by the student,
        by filtering against a `enrolled` query parameter in the URL.
        """

        queryset = super().get_queryset()
        queryset = queryset.select_related("category", "instructor")
        enrolled = self.request.query_params.get("enrolled", None)

        if (
            enrolled
            and self.request.user.is_authenticated
            and self.request.user.is_student
        ):
            queryset = queryset.filter(enrollments__student=self.request.user)

        return queryset

    def get_course_list_cache_key(self, request):
        """
        Generate a unique cache key for the course list API.

        The cache key is based on the query parameters and the user's authentication status.
        This ensures that different users or query parameter combinations have separate cache entries.
        """

        query_string = urlencode(request.GET, doseq=True)
        user_id = str(request.user.id) if request.user.is_authenticated else "anonymous"
        return f"course_list:{user_id}:{query_string}"

    def list(self, request, *args, **kwargs):
        """
        List all courses with caching and pagination.
        """

        cache_key = self.get_course_list_cache_key(request)
        cached_data = cache.get(cache_key)
        if cached_data:
            return self.ok(cached_data)

        response = super().list(request, *args, **kwargs)
        response_data = response.data
        cache.set(cache_key, response_data)

        return self.ok(response_data)

    def create(self, request, *args, **kwargs):
        """
        Create a new course by an instructor.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: The created course data.
        """

        serializer = CourseCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        data["instructor"] = (
            request.user if not request.user.is_superuser else data["instructor"]
        )
        course = CourseServices().handle_create_course(data=data)

        # Remove cache
        cache_keys = self.get_cache_key_by_regex("course_list:.*")
        self.delete_cache(cache_keys)

        response_data = self.serialize_data(course)
        return self.created(response_data)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a course by an instructor.
        Instructors can only update their own courses.
        Instructors cannot disable a course if it is in progress and has students enrolled in it.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: The updated course data.
        """

        instance = self.get_object()

        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.validated_data

        try:
            course = CourseServices().handle_partial_update(instance, serializer_data)
        except ValueError as e:
            return self.bad_request(field="status", message=str(e))

        response_data = self.serialize_data(course)

        # Remove cache, include top course
        cache_keys = self.get_cache_key_by_regex("course_list:.*")
        self.delete_cache(cache_keys=cache_keys + ["top_courses"])

        return self.ok(response_data)

    @action(detail=True, methods=["post"])
    def enroll(self, request, **kwargs):
        """
        Enroll a student in a course.

        Args:
            request (HttpRequest): The current request object.
        """
        serializer = EnrollmentCreateOrEditSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        course = self.get_object()

        try:
            CourseServices().handle_enrollment(
                user=request.user, course=course, data=serializer.validated_data
            )
        except CourseException as exc:
            return self.bad_request(field="course", message=str(exc.developer_message))
        except (UserException, EnrollmentException) as exc:
            return self.bad_request(field="student", message=str(exc.developer_message))

        enrollment_serializer = BaseSuccessResponseSerializer(
            {"data": {"success": True}}
        )
        return self.ok(enrollment_serializer.data)

    @action(detail=True, methods=["post"])
    def leave(self, request, **kwargs):
        """
        Allows a student to leave a course.

        This method allows a student to leave a course they are enrolled in.
        Instructors are not allowed to leave courses.
        """
        serializer = EnrollmentCreateOrEditSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        course = self.get_object()

        try:
            CourseServices().handle_leave_course(
                request.user, course, serializer.validated_data
            )
        except UserException as exc:
            return self.bad_request(field="student", message=str(exc.developer_message))
        except EnrollmentException as exc:
            return self.bad_request(field="course", message=str(exc.developer_message))

        response_serializer = BaseSuccessResponseSerializer({"data": {"success": True}})
        return self.ok(response_serializer.data)

    @extend_schema(
        description="View all students enrolled in a course.",
        responses={
            200: CourseStudentResponseSerializer,
            403: BaseForbiddenResponseSerializer,
            404: BaseNotFoundResponseSerializer,
        },
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="students",
        permission_classes=[IsAuthenticated, IsInstructor],
    )
    def get_students(self, request, **kwargs):
        """
        View all students enrolled in a course.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: A list of students enrolled in the course.
        """
        try:
            course = self.get_object()

            users = CourseServices().handle_get_students_of_course(course=course)

            paginator = self.paginator
            page = paginator.paginate_queryset(users, request)
            response_data = paginator.get_paginated_response(page).data
            serializer = self.get_serializer(
                {"data": response_data.get("data"), "meta": response_data.get("meta")}
            )
            return self.ok(serializer.data)

        except Exception as exc:
            return self.internal_server_error(message=f"{str(exc)}")

    @extend_schema(
        description="Get top courses based on the number of students enrolled.",
        responses={
            200: TopCoursesSerializer,
        },
    )
    @action(
        detail=False, methods=["get"], url_path="top", permission_classes=[AllowAny]
    )
    def get_top_courses(self, request):
        """
        Get top courses based on the number of students enrolled.
        """

        cache_key = "top_courses"
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return self.ok(cached_data)

            queryset = self.get_queryset()
            queryset = queryset.annotate(num_students=Count("enrollments"))
            queryset = queryset.order_by("-num_students")[: settings.TOP_COURSES_LIMIT]

            serializer = TopCoursesSerializer({"data": queryset})
            cache.set(cache_key, serializer.data)
            return self.ok(serializer.data)

        except Exception as exc:
            return self.internal_server_error(message=f"{str(exc)}")

    def get_cache_key_by_regex(self, pattern):
        """
        Get cache keys by regex.
        """

        redis_client = get_redis_connection("default")
        regex = re.compile(pattern)
        cursor = 0
        cache_keys = []

        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match="*", count=100)
            for key in keys:
                key_str = key.decode("utf-8")
                if regex.search(key_str):
                    cache_keys.append(key_str)
            if cursor == 0:
                break

        return cache_keys

    def delete_cache(self, cache_keys):
        """
        Delete cache by redis.
        """

        redis_client = get_redis_connection("default")
        if cache_keys:
            redis_client.delete(*cache_keys)


class CategoryViewSet(BaseGenericViewSet, CustomListModelMixin):
    """
    Category view set
    """

    permission_classes = [AllowAny]
    serializer_class = CategoryListSerializer
    resource_name = "categories"
    queryset = Category.objects.all().order_by("-modified")


apps = [CourseViewSet, CategoryViewSet]
