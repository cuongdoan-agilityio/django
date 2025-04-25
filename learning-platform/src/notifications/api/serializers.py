from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    """

    class Meta:
        model = Notification
        fields = ["id", "user", "message"]
        read_only_fields = ["user"]
