from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny

from core.api_views import BaseGenericViewSet
from .serializers import NotificationSerializer


class NotificationViewSet(
    BaseGenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
):
    """
    A viewset for handling notifications.
    This viewset allows users to list, retrieve, and update their notifications.
    """

    permission_classes = [AllowAny]
    serializer_class = NotificationSerializer
    http_method_names = ["get", "patch"]
    resource_name = "notifications"

    def get_queryset(self):
        """
        Returns the queryset for the Notification model.
        """
        return self.request.user.notifications.all()

    def list(self, request, *args, **kwargs):
        """
        Returns a list of notifications for the authenticated user.
        """

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Returns a single notification for the authenticated user.
        """

        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates a notification for the authenticated user.
        """

        return super().partial_update(request, *args, **kwargs)


apps = [NotificationViewSet]
