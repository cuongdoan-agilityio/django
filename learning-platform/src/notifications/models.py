from django.db import models
from core.models import AbstractBaseModel

from django.conf import settings


class Notification(AbstractBaseModel):
    """
    Model representing a notification.

    Attributes:
        id (int): Unique identifier for the notification.
        user (ForeignKey): The user associated with the notification.
        message (str): The message content of the notification.
        is_read (bool): Indicates whether the notification has been read or not.
    """

    message = models.TextField()
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )

    def __str__(self):
        return f"Notification for {self.user.username}"
