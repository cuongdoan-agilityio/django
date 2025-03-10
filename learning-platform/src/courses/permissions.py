from rest_framework.permissions import BasePermission


class CoursePermission(BasePermission):
    """
    Custom permission to handle all actions: students, partial_update, create, enroll, leave.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to perform the action.
        """

        if view.action in ["create", "partial_update", "students"]:
            return request.user.is_authenticated and hasattr(
                request.user, "instructor_profile"
            )

        if view.action in ["enroll", "leave"]:
            return request.user.is_authenticated and hasattr(
                request.user, "student_profile"
            )

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to perform the action on the object.
        """

        if view.action in ["partial_update", "students"]:
            return obj.instructor == request.user.instructor_profile

        return True
