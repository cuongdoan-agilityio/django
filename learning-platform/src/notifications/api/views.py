from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from core.api_views import BaseGenericViewSet
from rest_framework.mixins import UpdateModelMixin
from core.permissions import IsOwner
from core.mixins import CustomListModelMixin, CustomRetrieveModelMixin
from core.serializers import (
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseNotFoundResponseSerializer,
)
from notifications.models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationDetailSerializer,
)
from notifications.services import NotificationServices


class NotificationFilter(filters.FilterSet):
    """
    FilterSet for filtering notifications by the `is_read` field.
    """

    is_read = filters.BooleanFilter(field_name="is_read")

    class Meta:
        model = Notification
        fields = ["is_read"]


@extend_schema_view(
    list=extend_schema(
        description="List all user notifications with optional filtering by `is_read`.",
        parameters=[
            OpenApiParameter(
                name="is_read",
                description="Filter notifications by their read status (true/false).",
                required=False,
                type=bool,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: NotificationListSerializer,
            400: BaseBadRequestResponseSerializer,
        },
    ),
    retrieve=extend_schema(
        description="Retrieve a user notification.",
        responses={
            200: NotificationDetailSerializer,
            401: BaseForbiddenResponseSerializer,
            404: BaseNotFoundResponseSerializer,
        },
    ),
)
class NotificationViewSet(
    BaseGenericViewSet, CustomListModelMixin, CustomRetrieveModelMixin, UpdateModelMixin
):
    """
    A viewset for handling notifications.
    This viewset allows users to list, retrieve, and update their notifications.
    """

    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ["get", "patch"]
    resource_name = "notifications"
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter

    def get_queryset(self):
        """
        Returns the queryset for the user notification.
        """

        return self.request.user.notifications.all().order_by("-modified")

    def get_serializer_class(self):
        """
        Returns the serializer class based on the action.
        """

        if self.action == "list":
            return NotificationListSerializer
        return NotificationDetailSerializer

    @extend_schema(
        description="Update a user notification.",
        request=NotificationSerializer,
        responses={
            200: NotificationDetailSerializer,
            400: BaseBadRequestResponseSerializer,
            401: BaseForbiddenResponseSerializer,
            404: BaseNotFoundResponseSerializer,
        },
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a user notification.

        This method allows the user to update specific fields of a notification, such as the `is_read` status.
        The update logic is delegated to the `NotificationServices` class for better separation of concerns.
        """

        serializer = NotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()

        notification = NotificationServices().handle_partial_update(
            instance, serializer.validated_data
        )

        serializer = NotificationDetailSerializer({"data": notification})
        return self.ok(serializer.data)


apps = [NotificationViewSet]
