import re
from django.core.cache import cache
from django_redis import get_redis_connection
import django_filters
from rest_framework import filters
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
from rest_framework.permissions import AllowAny
from urllib.parse import urlencode

from accounts.api.serializers import UserBaseSerializer
from core.api_views import BaseGenericViewSet
from core.serializers import (
    BaseSuccessResponseSerializer,
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseNotFoundResponseSerializer,
)
from core.error_messages import ErrorMessage
from core.mixins import FormatDataMixin
from courses.permissions import CoursePermission
from notifications.models import Notification
from notifications.constants import NotificationMessage

from .response_schema import course_response_schema, student_list_response_schema

from ..models import Course, Category
from .serializers import (
    CourseCreateSerializer,
    CourseDataSerializer,
    CourseUpdateSerializer,
    CategorySerializer,
    EnrollmentCreateOrEditSerializer,
    EnrollmentSerializer,
    TopCoursesSerializer,
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
    get_students=extend_schema(
        description="View all students enrolled in a course.",
        responses={
            200: student_list_response_schema,
            403: BaseForbiddenResponseSerializer,
            404: BaseNotFoundResponseSerializer,
        },
    ),
    get_top_courses=extend_schema(
        description="Get top courses based on the number of students enrolled.",
        responses={
            200: TopCoursesSerializer,
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
            return UserBaseSerializer
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

        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_superuser:
            if "instructor" not in serializer.validated_data:
                return self.bad_request(
                    field="instructor", message=ErrorMessage.INSTRUCTOR_DATA_REQUIRED
                )

            course = serializer.save()
        else:
            course = serializer.save(
                instructor=request.user,
            )

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

        # Check if the course is in progress and has students enrolled
        if "status" in serializer_data and serializer_data["status"] == "inactive":
            if instance.enrollments.exists():
                return self.bad_request(
                    field="status", message=ErrorMessage.COURSE_HAS_STUDENTS
                )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
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
        serializer = EnrollmentCreateOrEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = self.get_object()

        if request.user.is_superuser:
            if "student" not in request.data:
                return self.bad_request(
                    field="student", message=ErrorMessage.STUDENT_DATA_REQUIRED
                )
            try:
                student = User.objects.get(id=request.data["student"])
            except User.DoesNotExist:
                return self.bad_request(
                    field="student", message=ErrorMessage.INVALID_USER_ID
                )
        else:
            student = request.user

        enrollment_serializer = EnrollmentSerializer(
            data={
                "course": str(course.id),
                "student": str(student.id),
            }
        )
        enrollment_serializer.is_valid(raise_exception=True)
        course.students.add(student)

        # Create notification.
        Notification.objects.create(
            user=course.instructor,
            message=NotificationMessage.STUDENT_ENROLLED.format(
                user_name=student.username, course_name=course.title
            ),
        )

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
        serializer = EnrollmentCreateOrEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = self.get_object()
        if request.user.is_superuser:
            if "student" not in request.data:
                return self.bad_request(
                    field="student", message=ErrorMessage.STUDENT_DATA_REQUIRED
                )
            try:
                student = User.objects.get(id=request.data["student"])
            except User.DoesNotExist:
                return self.bad_request(
                    field="student",
                    message=ErrorMessage.INVALID_USER_ID,
                )
        else:
            student = request.user

        if enrollment := student.enrollments.filter(course=course).first():
            enrollment.delete()

            # Create notification.
            Notification.objects.create(
                user=student,
                message=NotificationMessage.STUDENT_UNENROLLED.format(
                    course_name=course.title
                ),
            )
            response_serializer = BaseSuccessResponseSerializer(
                {"data": {"success": True}}
            )
            return self.ok(response_serializer.data)
        else:
            return self.bad_request(
                field="detail", message=ErrorMessage.STUDENT_NOT_ENROLLED
            )

    @action(detail=True, methods=["get"], url_path="students")
    def get_students(self, request, **kwargs):
        """
        View all students enrolled in a course.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: A list of students enrolled in the course.
        """

        course = self.get_object()

        users = User.objects.filter(enrollments__course=course).distinct()

        paginator = self.paginator
        page = paginator.paginate_queryset(users, request)
        serializer = self.get_serializer(page, many=True)
        response_data = paginator.get_paginated_response(serializer.data).data

        return self.ok(response_data)

    @action(detail=False, methods=["get"], url_path="top")
    def get_top_courses(self, request):
        """
        Get top courses based on the number of students enrolled.
        """

        cache_key = "top_courses"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return self.ok(cached_data)

        queryset = self.get_queryset()
        queryset = queryset.annotate(num_students=Count("enrollments"))
        queryset = queryset.order_by("-num_students")[: settings.TOP_COURSES_LIMIT]

        response_data = self.format_list_data(queryset)
        cache.set(cache_key, response_data)
        return self.ok(response_data)

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


class CategoryViewSet(BaseGenericViewSet, ListModelMixin):
    """
    Category view set
    """

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    resource_name = "categories"
    queryset = Category.objects.all()


apps = [CourseViewSet, CategoryViewSet]
