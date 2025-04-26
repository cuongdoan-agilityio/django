from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from core.api_views import BaseGenericViewSet
from core.permissions import IsOwner
from core.serializers import BaseDetailSerializer
from notifications.models import Notification
from notifications.api.response_schema import notification_detail_response_schema
from .serializers import NotificationSerializer


from rest_framework.response import Response


class RetrieveResponseMixin:
    """
    A mixin to provide a consistent response structure for retrieve methods.
    """

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve an object and wrap the response in a consistent structure.
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "data": serializer.data,
            }
        )


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
    )
)
class NotificationViewSet(
    BaseGenericViewSet,
    ListModelMixin,
    RetrieveResponseMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
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

    # @extend_schema(
    #     description="Retrieve a user notification.",
    #     responses={
    #         200: notification_detail_response_schema,
    #     },
    # )
    # def retrieve(self, request, *args, **kwargs):
    #     self.serializer_class = NotificationSerializer
    #     notification = super().retrieve(request, *args, **kwargs)
    #     serializer = BaseDetailSerializer(
    #         notification.data, context={"serializer_class": self.get_serializer_class()}
    #     )
    #     return self.ok(serializer.data)

    @extend_schema(
        description="Retrieve a user notification.",
        responses={
            200: notification_detail_response_schema,
        },
    )
    def partial_update(self, request, *args, **kwargs):
        notification = super().partial_update(request, *args, **kwargs)
        serializer = BaseDetailSerializer(
            notification.data, context={"serializer_class": self.get_serializer_class()}
        )
        return self.ok(serializer.data)


apps = [NotificationViewSet]
