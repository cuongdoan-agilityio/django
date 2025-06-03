import pytest
from django.core.exceptions import ValidationError

from notifications.factories import NotificationFactory
from notifications.models import Notification
from core.test import BaseAPITestCase


class TestNotificationModel(BaseAPITestCase):
    """
    Test case for the Notification model.
    """

    def test_create_notification_success(
        self, fake_notification, fake_user, share_data
    ):
        """
        Test that a notification can be created successfully.
        """

        assert fake_notification.user == fake_user
        assert fake_notification.message == share_data["message"]
        assert fake_notification.is_read == share_data["is_read"]

    def test_create_notification_without_user(self):
        """
        Test that a notification cannot be created without a user.
        """

        with pytest.raises(ValidationError):
            notification = Notification(
                message="This is a test notification.",
                is_read=False,
                user=None,
            )
            notification.full_clean()

    def test_create_notification_without_message(self, fake_user):
        """
        Test that a notification cannot be created without a message.
        """

        with pytest.raises(ValidationError):
            notification = Notification(
                user=fake_user,
                is_read=False,
                message=None,
            )
            notification.full_clean()

    def test_create_notification_with_empty_message(self, fake_user):
        """
        Test that a notification cannot be created with an empty message.
        """

        with pytest.raises(ValidationError):
            notification = Notification(
                user=fake_user,
                message="",
                is_read=False,
            )
            notification.full_clean()

    def test_mark_notification_as_read(self, fake_user):
        """
        Test that a notification can be marked as read.
        """

        notification = NotificationFactory(
            user=fake_user,
            is_read=False,
        )
        notification.is_read = True
        notification.save()
        assert notification.is_read is True

    def test_mark_notification_as_unread(self, fake_user):
        """
        Test that a notification can be marked as unread.
        """

        notification = NotificationFactory(
            user=fake_user,
        )
        notification.is_read = False
        notification.save()
        assert notification.is_read is False

    def test_notification_str(self, fake_notification, fake_user):
        """
        Test the string representation of the notification.
        """

        assert str(fake_notification) == f"Notification for {fake_user.username}"

    def test_notification_message_help_text(self, fake_notification):
        """
        Test the help text for the notification message field.
        """

        field_help_text = fake_notification._meta.get_field("message").help_text
        assert field_help_text == "Notification message"
