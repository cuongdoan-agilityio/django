from rest_framework import filters
import django_filters
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from django.db.models import Count
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.permissions import AllowAny

from accounts.api.serializers import UserBaseSerializer
from core.api_views import BaseModelViewSet, BaseGenericViewSet
from core.serializers import (
    BaseSuccessResponseSerializer,
    BaseListSerializer,
    BaseDetailSerializer,
    BaseBadRequestResponseSerializer,
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
)
class CourseViewSet(BaseModelViewSet, FormatDataMixin):
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

    def get_queryset(self):
        """
        Optionally restricts the returned courses to those enrolled by the student,
        by filtering against a `enrolled` query parameter in the URL.
        """

        queryset = super().get_queryset()
        enrolled = self.request.query_params.get("enrolled", None)

        if (
            enrolled
            and self.request.user.is_authenticated
            and self.request.user.is_student
        ):
            queryset = queryset.filter(enrollments__student=self.request.user)

        return queryset

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

        response_data = self.format_data(course)
        return self.created(response_data)

    @extend_schema(
        description="Retrieve a single course",
        responses={
            200: course_response_schema,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single course with custom response format.

        Returns:
            Response: The course data.
        """

        course = self.get_object()
        serializer = BaseDetailSerializer(
            course, context={"serializer_class": CourseDataSerializer}
        )
        return self.ok(serializer.data)

    @extend_schema(
        description="Enroll a student in a course.",
        request=CourseUpdateSerializer,
        responses={200: course_response_schema, 400: BaseBadRequestResponseSerializer},
    )
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
                return self.bad_request(ErrorMessage.COURSE_HAS_STUDENTS)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        data = BaseDetailSerializer(
            course, context={"serializer_class": CourseDataSerializer}
        )
        return self.ok(data.data)

    @extend_schema(
        description="Enroll a student in a course.",
        request=EnrollmentCreateOrEditSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            400: BaseBadRequestResponseSerializer,
        },
    )
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
                return self.bad_request({"student": ErrorMessage.STUDENT_DATA_REQUIRED})
            try:
                student = User.objects.get(id=request.data["student"])
            except User.DoesNotExist:
                return self.bad_request({"student": ErrorMessage.INVALID_USER_ID})
        else:
            student = request.user

        enrollment_serializer = EnrollmentSerializer(
            data={
                "course": str(course.id),
                "student": str(student.id),
            }
        )
        enrollment_serializer.is_valid(raise_exception=True)
        enrollment_serializer.save()

        # Send notification.
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

    @extend_schema(
        description="Leave a course.",
        request=EnrollmentCreateOrEditSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            400: BaseBadRequestResponseSerializer,
        },
    )
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
                return self.bad_request({"student": ErrorMessage.STUDENT_DATA_REQUIRED})
            try:
                student = User.objects.get(id=request.data["student"])
            except User.DoesNotExist:
                return self.bad_request({"student": ErrorMessage.INVALID_USER_ID})
        else:
            student = request.user

        if enrollment := student.enrollments.filter(course=course).first():
            enrollment.delete()

            # Send notification.
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
            return self.bad_request(ErrorMessage.STUDENT_NOT_ENROLLED)

    @extend_schema(
        description="View all students enrolled in a course.",
        responses={200: student_list_response_schema},
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

        enrollments = course.enrollments.all()
        users = [enrollment.student for enrollment in enrollments]

        paginator = self.paginator
        page = paginator.paginate_queryset(users, request)
        serializer = BaseListSerializer(
            paginator.get_paginated_response(page).data,
            context={"serializer_class": UserBaseSerializer},
        )
        return self.ok(serializer.data)

    @extend_schema(
        description="Get top courses based on the number of students enrolled.",
        responses={
            200: TopCoursesSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="top")
    def get_top_courses(self, request):
        """
        Get top courses based on the number of students enrolled.
        """
        queryset = self.get_queryset()
        queryset = queryset.annotate(num_students=Count("enrollments"))
        queryset = queryset.order_by("-num_students")[: settings.TOP_COURSES_LIMIT]

        serialized_data = CourseDataSerializer(queryset, many=True).data

        return self.ok({"data": serialized_data})


class CategoryViewSet(BaseGenericViewSet, ListModelMixin):
    """
    Category view set
    """

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    http_method_names = ["get"]
    resource_name = "categories"

    def get_queryset(self):
        return Category.objects.all()


apps = [CourseViewSet, CategoryViewSet]
