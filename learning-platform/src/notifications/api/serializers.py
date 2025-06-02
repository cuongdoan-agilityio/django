from rest_framework import serializers

from core.serializers import MetaSerializer
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    """

    class Meta:
        model = Notification
        fields = ["id", "is_read", "message", "modified"]


class NotificationDataSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    """

    class Meta:
        model = Notification
        fields = ["id", "is_read", "message", "modified"]


class NotificationListSerializer(serializers.Serializer):
    """
    Serializer for the Notification model.
    """

    data = NotificationDataSerializer(many=True)
    meta = MetaSerializer(required=False)
