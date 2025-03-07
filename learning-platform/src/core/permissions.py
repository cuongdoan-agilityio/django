from rest_framework.permissions import BasePermission


class IsInstructorAndOwner(BasePermission):
    """
    Custom permission to only allow instructors to update their own courses.
    """

    def has_permission(self, request, view) -> bool:
        """
        Check if the user is an instructor.
        """

        if not hasattr(request.user, "instructor_profile"):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the owner of the course.
        """

        return obj.instructor == request.user.instructor_profile


class IsStudent(BasePermission):
    """
    Custom permission to validate user is student.
    """

    def has_permission(self, request, view) -> bool:
        """
        Check if the user is an student.
        """

        if not hasattr(request.user, "student_profile"):
            return False

        return True
