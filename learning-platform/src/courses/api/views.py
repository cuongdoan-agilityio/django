from rest_framework import filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from core.api_views import BaseModelViewSet
from core.serializers import BaseSuccessResponseSerializer
from core.pagination import CustomPagination
from students.models import Student
from enrollments.models import Enrollment
from students.api.serializers import StudentListSerializer

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
    - Students can see the courses they are enrolled in (add filter with enrolled=true).
    - Can filter courses with "course category" and "courses status".

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
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status", "instructor"]
    search_fields = ["title", "description"]

    def get_permissions(self):
        """
        Get permissions for Course APIs.
        """

        if self.action in ["create", "partial_update", "enroll", "leave", "students"]:
            return [IsAuthenticated()]

        return super().get_permissions()

    def get_queryset(self):
        """
        Optionally restricts the returned courses to those enrolled by the student,
        by filtering against a `enrolled` query parameter in the URL.
        """

        queryset = super().get_queryset()
        enrolled = self.request.query_params.get("enrolled", None)
        if enrolled and not self.request.user.is_instructor:
            student = Student.objects.get(user=self.request.user)
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
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.ok(
            {
                "data": serializer.data,
                "meta": {
                    "pagination": {
                        "total": queryset.count(),
                        "limit": self.paginator.get("limit"),
                        "offset": self.paginator.get("offset"),
                    }
                },
            }
        )

    @extend_schema(
        description="Retrieve a single course",
        request=CourseCreateSerializer,
        responses={
            200: OpenApiResponse(
                response=CourseSerializer,
                examples=[
                    OpenApiExample(
                        "Example response",
                        summary="Example response",
                        value={
                            "data": {
                                "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "title": "string",
                                "description": "string",
                                "category": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "instructor": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "status": "activate",
                            }
                        },
                    )
                ],
            )
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

        if not request.user.is_instructor:
            return self.forbidden()

        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.save(
            instructor=request.user.instructor_profile,
        )

        course_serializer = CourseSerializer({"data": course})
        return self.created(course_serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single course with custom response format.

        Returns:
            Response: The course data.
        """

        pk = kwargs.get("pk")
        if course := Course.objects.filter(uuid=pk).first():
            serializer = CourseSerializer({"data": course})
            return self.ok(serializer.data)
        else:
            return self.not_found()

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

        if not request.user.is_instructor:
            return self.forbidden()

        instance = self.get_object()

        # Ensure the instructor can only update their own courses
        if (
            not request.user.is_authenticated
            or not hasattr(request.user, "instructor_profile")
            or instance.instructor != request.user.instructor_profile
        ):
            return self.forbidden(
                {"detail": "You do not have permission to update this course."}
            )

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

        if request.user.is_instructor:
            return self.forbidden({"detail": "Instructors cannot enroll course."})

        course = Course.objects.get(uuid=kwargs.get("pk"))

        if course.status != "activate" or not course.instructor:
            return self.bad_request("This course is not available for enrollment.")

        student = Student.objects.get(user=request.user)

        if Enrollment.objects.filter(course=course, student=student).exists():
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

        if request.user.is_instructor:
            return self.forbidden({"detail": "Instructors cannot leave course."})

        course = Course.objects.get(uuid=kwargs.get("pk"))
        student = Student.objects.get(user=request.user)
        if enrollment := Enrollment.objects.filter(
            course=course, student=student
        ).first():
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
                response=StudentListSerializer,
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

        if not request.user.is_instructor:
            return self.forbidden(
                {"detail": "Only instructors can view enrolled students."}
            )

        course = Course.objects.get(uuid=kwargs.get("pk"))

        if course.instructor != request.user.instructor_profile:
            return self.forbidden(
                {
                    "detail": "You do not have permission to view the students of this course."
                }
            )

        enrollments = Enrollment.objects.filter(course=course)
        users = [enrollment.student.user for enrollment in enrollments]
        paginator = self.paginator
        page = paginator.paginate_queryset(users, request)
        serializer = StudentListSerializer(paginator.get_paginated_response(page).data)
        return self.ok(serializer.data)


apps = [CourseViewSet]
