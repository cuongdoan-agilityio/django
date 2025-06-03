from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Custom permission to ensure the user can only access their own.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the instance belongs to the authenticated user
        """

        return obj.user == request.user


class IsAdminOrOwner(BasePermission):
    """
    Custom permission to allow only admins or the owner of the profile to update it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is an admin or the owner of the object.
        """

        if request.user.is_superuser:
            return True

        return obj.id == request.user.id


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
