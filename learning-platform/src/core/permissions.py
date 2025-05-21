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
