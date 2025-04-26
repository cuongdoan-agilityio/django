from rest_framework import serializers

from notifications.models import Notification

from core.serializers import BaseDetailResponseSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    """

    class Meta:
        model = Notification
        fields = ["id", "is_read", "message"]


class NotificationDetailSerializer(BaseDetailResponseSerializer):
    data = NotificationSerializer()
