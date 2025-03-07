from rest_framework import filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from core.api_views import BaseModelViewSet
from core.serializers import BaseSuccessResponseSerializer, BaseListSerializer
from core.permissions import IsInstructorAndOwner, IsStudent
from students.models import Student
from enrollments.models import Enrollment
from students.api.serializers import StudentBaseSerializer

from ..models import Course
from .serializers import (
    CourseSerializer,
    CourseCreateSerializer,
    CourseDataSerializer,
    CourseUpdateSerializer,
)


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
    permission_classes = [AllowAny]
    http_method_names = ["get", "post", "patch"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["title", "description"]

    def get_permissions(self):
        """
        Get permissions for Course APIs.
        """

        if self.action in ["students", "partial_update", "create"]:
            return [IsAuthenticated(), IsInstructorAndOwner()]

        if self.action in ["enroll", "leave"]:
            return [IsAuthenticated(), IsStudent()]

        return super().get_permissions()

    def get_queryset(self):
        """
        Optionally restricts the returned courses to those enrolled by the student,
        by filtering against a `enrolled` query parameter in the URL.
        """

        queryset = super().get_queryset()
        enrolled = self.request.query_params.get("enrolled", None)
        if enrolled and not self.request.user.is_instructor:
            student = Student.objects.filter(user=self.request.user).first()
            queryset = queryset.filter(enrollments__student=student)
        return queryset

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
        responses={201: CourseSerializer},
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

        course = serializer.save(
            instructor=request.user.instructor_profile,
        )

        course_serializer = CourseSerializer({"data": course})
        return self.created(course_serializer.data)

    @extend_schema(
        description="Retrieve a single course",
        responses={
            200: CourseSerializer,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single course with custom response format.

        Returns:
            Response: The course data.
        """

        course = self.get_object()
        serializer = CourseSerializer({"data": course})
        return self.ok(serializer.data)

    @extend_schema(
        description="Enroll a student in a course.",
        request=CourseUpdateSerializer,
        responses={
            200: CourseSerializer,
        },
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
                return self.bad_request(
                    "Cannot disable a course that is in progress and has students enrolled."
                )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return self.ok(CourseSerializer({"data": course}).data)

    @extend_schema(
        description="Enroll a student in a course.",
        request=None,
        responses={
            200: BaseSuccessResponseSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def enroll(self, request, **kwargs):
        """
        Enroll a student in a course.

        Args:
            request (HttpRequest): The current request object.
        """

        course = self.get_object()

        if course.status != "activate" or not course.instructor:
            return self.bad_request("This course is not available for enrollment.")

        student = Student.objects.get(user=request.user)

        if student.enrollments.filter(course=course).exists():
            return self.bad_request("You are already enrolled in this course.")

        Enrollment.objects.create(course=course, student=student)
        enrollment_serializer = BaseSuccessResponseSerializer(
            {"data": {"success": True}}
        )
        return self.ok(enrollment_serializer.data)

    @extend_schema(
        description="Leave a course.",
        request=None,
        responses={
            200: BaseSuccessResponseSerializer,
        },
    )
    @action(detail=True, methods=["post"])
    def leave(self, request, **kwargs):
        """
        Allows a student to leave a course.

        This method allows a student to leave a course they are enrolled in.
        Instructors are not allowed to leave courses.
        """

        course = self.get_object()
        student = Student.objects.filter(user=request.user).first()

        if enrollment := student.enrollments.filter(course=course).first():
            enrollment.delete()
            response_serializer = BaseSuccessResponseSerializer(
                {"data": {"success": True}}
            )
            return self.ok(response_serializer.data)
        else:
            return self.bad_request("You are not enrolled in this course.")

    @extend_schema(
        description="View all students enrolled in a course.",
        responses={
            200: OpenApiResponse(
                response=BaseListSerializer,
                examples=[
                    OpenApiExample(
                        "Example response",
                        summary="Example response",
                        value={
                            "data": [
                                {
                                    "uuid": "string",
                                    "username": "string",
                                    "first_name": "string",
                                    "last_name": "string",
                                    "email": "user@example.com",
                                }
                            ],
                            "meta": {
                                "pagination": {"total": 1, "limit": 20, "offset": 0}
                            },
                        },
                    )
                ],
            )
        },
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


apps = [CourseViewSet]
