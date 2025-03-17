from rest_framework import filters
import django_filters
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import AllowAny

from core.api_views import BaseModelViewSet, BaseGenericViewSet
from core.serializers import (
    BaseSuccessResponseSerializer,
    BaseListSerializer,
    BaseDetailSerializer,
    BaseBadRequestResponseSerializer,
)
from core.exceptions import ErrorMessage
from courses.permissions import CoursePermission
from students.models import Student
from students.api.serializers import StudentBaseSerializer

from .response_schema import course_response_schema, student_list_response_schema

from ..models import Course, Category, Enrollment
from .serializers import (
    CourseCreateSerializer,
    CourseDataSerializer,
    CourseUpdateSerializer,
    CategorySerializer,
    EnrollmentCreateOrEditSerializer,
    EnrollmentSerializer,
)


class CustomFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(method="filter_status")
    category = django_filters.UUIDFilter(field_name="category__uuid")

    def filter_status(self, queryset, name, value):
        status_list = value.split(",")
        return queryset.filter(status__in=status_list)

    class Meta:
        model = Course
        fields = ["category"]


class CourseViewSet(BaseModelViewSet):
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
            student = Student.objects.filter(user=self.request.user).first()
            queryset = queryset.filter(enrollments__student=student)

        return queryset

    @extend_schema(
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
    )
    def list(self, request, *args, **kwargs):
        """
        List all courses with pagination and custom response format.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: A paginated list of courses with metadata.
        """

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        data = self.get_paginated_response(page).data
        serializer = BaseListSerializer(
            data, context={"serializer_class": CourseDataSerializer}
        )
        return self.ok(serializer.data)

    @extend_schema(
        description="Create a course.",
        request=CourseCreateSerializer,
        responses={
            201: course_response_schema,
        },
    )
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
                    {"instructor": ErrorMessage.INSTRUCTOR_DATA_REQUIRED}
                )

            course = serializer.save()
        else:
            course = serializer.save(
                instructor=request.user.instructor_profile,
            )

        course_serializer = BaseDetailSerializer(
            course, context={"serializer_class": CourseDataSerializer}
        )
        return self.created(course_serializer.data)

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
            if Enrollment.objects.filter(
                course=instance, course__status="activate"
            ).exists():
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
            404: BaseBadRequestResponseSerializer,
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
            student = request.data["student"]
        else:
            student = Student.objects.filter(user=request.user).first().uuid

        enrollment_serializer = EnrollmentSerializer(
            data={
                "course": str(course.uuid),
                "student": str(student),
            }
        )
        enrollment_serializer.is_valid(raise_exception=True)
        enrollment_serializer.save()
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
            student = Student.objects.filter(uuid=request.data["student"]).first()
        else:
            student = Student.objects.filter(user=request.user).first()

        if enrollment := student.enrollments.filter(course=course).first():
            enrollment.delete()
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
    @action(detail=True, methods=["get"])
    def students(self, request, **kwargs):
        """
        View all students enrolled in a course.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: A list of students enrolled in the course.
        """

        course = self.get_object()

        enrollments = Enrollment.objects.filter(course=course)
        users = [enrollment.student.user for enrollment in enrollments]

        paginator = self.paginator
        page = paginator.paginate_queryset(users, request)
        serializer = BaseListSerializer(
            paginator.get_paginated_response(page).data,
            context={"serializer_class": StudentBaseSerializer},
        )
        return self.ok(serializer.data)


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
