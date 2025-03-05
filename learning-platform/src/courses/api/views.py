from rest_framework.permissions import AllowAny

from core.api_views import BaseModelViewSet
from ..models import Course
from .serializers import CourseSerializer
from students.models import Student

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from core.pagination import CustomPagination
from enrollments.models import Enrollment


class CourseViewSet(BaseModelViewSet):
    """
    Course view set

    - People who do not need to log in can still see.
    - Students can see the courses they are enrolled in (add filter with enrolled=true).
    - Can filter courses with "course category" and "courses status".

    Filters:
        - category: Filter courses by category.
        - status: Filter courses by status.
        - enrolled: Filter courses by enrollment status (students only).

    Returns:
        Response: A paginated list of courses with metadata.
    """

    resource_name = "courses"
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ["get"]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        """
        Optionally restricts the returned courses to those enrolled by the student,
        by filtering against a `enrolled` query parameter in the URL.
        """
        queryset = super().get_queryset()
        enrolled = self.request.query_params.get("enrolled", None)
        if enrolled is not None and self.request.user.is_authenticated:
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
                        "limit": self.paginator.page_size,
                        "page": self.paginator.page.start_index(),
                    }
                },
            }
        )

    def create(self, request, *args, **kwargs):
        """
        Create a new course by an instructor.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: The created course data.
        """

        if not request.user.is_authenticated or not hasattr(
            request.user, "instructor_profile"
        ):
            return self.forbidden()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.created({"data": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single course with custom response format.

        Returns:
            Response: The course data.
        """
        pk = kwargs.get("pk")

        if course := Course.objects.filter(uuid=pk).first():
            serializer = self.get_serializer(course)
            return self.ok({"data": serializer.data})
        else:
            return self.not_found()

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a course by an instructor. Instructors can only update their own courses.
        Instructors cannot disable a course if it is in progress and has students enrolled in it.

        Args:
            request (HttpRequest): The current request object.

        Returns:
            Response: The updated course data.
        """
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

        # Check if the course is in progress and has students enrolled
        if "status" in request.data and request.data["status"] == "inactive":
            if Enrollment.objects.filter(
                course=instance, status="in_progress"
            ).exists():
                return self.bad_request(
                    {
                        "detail": "Cannot disable a course that is in progress and has students enrolled."
                    }
                )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.ok({"data": serializer.data})


apps = [CourseViewSet]
