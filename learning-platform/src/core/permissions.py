from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Custom permission to ensure the user can only access their own.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the instance belongs to the authenticated user
        """

        return (obj == request.user) or (obj.user == request.user)


class IsInstructor(BasePermission):
    """
    Custom permission to allow only instructor.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to perform the action.
        """

        if request.user.is_instructor:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to perform the action on the object.
        """

        if obj.instructor == request.user:
            return True

        return False


class IsStudent(BasePermission):
    """
    Custom permission to allow only student.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to perform the action.
        """

        if request.user.is_student:
            return True

        return False
