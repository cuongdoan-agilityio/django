from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from core.api_views import BaseModelViewSet
from core.permissions import IsOwner
from core.serializers import (
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseNotFoundResponseSerializer,
)
from core.mixins import CustomRetrieveModelMixin, CustomUpdateModelMixin
from notifications.models import Notification
from notifications.api.response_schema import notification_detail_response_schema
from .serializers import NotificationSerializer


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
    ),
    retrieve=extend_schema(
        description="Retrieve a user notification.",
        responses={
            200: notification_detail_response_schema,
            401: BaseForbiddenResponseSerializer,
            404: BaseNotFoundResponseSerializer,
        },
    ),
    partial_update=extend_schema(
        description="Update a user notification.",
        responses={
            200: notification_detail_response_schema,
            400: BaseBadRequestResponseSerializer,
            401: BaseForbiddenResponseSerializer,
            404: BaseNotFoundResponseSerializer,
        },
    ),
)
class NotificationViewSet(
    CustomRetrieveModelMixin, CustomUpdateModelMixin, BaseModelViewSet
):
    """
    A viewset for handling notifications.
    This viewset allows users to list, retrieve, and update their notifications.
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = NotificationSerializer
    http_method_names = ["get", "patch"]
    resource_name = "notifications"
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter

    def get_queryset(self):
        """
        Returns the queryset for the Notification model.
        """
        return self.request.user.notifications.all()


apps = [NotificationViewSet]
