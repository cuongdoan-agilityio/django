from rest_framework.permissions import BasePermission


class CoursePermission(BasePermission):
    """
    Custom permission to handle all actions: students, partial_update, create, enroll, leave.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to perform the action.
        """

        if request.user.is_superuser or view.action in ["list", "retrieve"]:
            return True

        if view.action in ["create", "partial_update", "get_students"]:
            return request.user.is_authenticated and request.user.is_instructor

        if view.action in ["enroll", "leave"]:
            return request.user.is_authenticated and request.user.is_student

        return False

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to perform the action on the object.
        """

        if request.user.is_superuser or view.action in ["retrieve"]:
            return True

        if view.action in ["partial_update", "get_students"]:
            return obj.instructor == request.user

        return False
