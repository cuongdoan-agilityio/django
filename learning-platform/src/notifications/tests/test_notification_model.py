from core.tests.base import BaseTestCase
from django.core.exceptions import ValidationError

from notifications.factories import NotificationFactory
from notifications.models import Notification


class NotificationModelTestCase(BaseTestCase):
    """
    Test case for the Notification model.
    """

    def setUp(self):
        """
        Set up the test case.
        """

        super().setUp()

        self.message = self.fake.sentence()
        self.is_read = self.fake.boolean()
        self.notification = NotificationFactory(
            user=self.user,
            message=self.message,
            is_read=self.is_read,
        )

    def test_create_notification_success(self):
        """
        Test that a notification can be created successfully.
        """

        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.message, self.message)
        self.assertEqual(self.notification.is_read, self.is_read)

    def test_create_notification_without_user(self):
        """
        Test that a notification cannot be created without a user.
        """

        with self.assertRaises(ValidationError):
            notification = Notification(
                message="This is a test notification.",
                is_read=False,
                user=None,
            )
            notification.full_clean()

    def test_create_notification_without_message(self):
        """
        Test that a notification cannot be created without a message.
        """

        with self.assertRaises(ValidationError):
            notification = Notification(
                user=self.user,
                is_read=False,
                message=None,
            )
            notification.full_clean()

    def test_create_notification_with_empty_message(self):
        """
        Test that a notification cannot be created with an empty message.
        """

        with self.assertRaises(ValidationError):
            notification = Notification(
                user=self.user,
                message="",
                is_read=False,
            )
            notification.full_clean()

    def test_mark_notification_as_read(self):
        """
        Test that a notification can be marked as read.
        """

        notification = NotificationFactory(
            user=self.user,
            message=self.message,
            is_read=False,
        )
        notification.is_read = True
        notification.save()
        self.assertTrue(notification.is_read)

    def test_mark_notification_as_unread(self):
        """
        Test that a notification can be marked as unread.
        """

        notification = NotificationFactory(
            user=self.user,
            message=self.message,
        )
        notification.is_read = False
        notification.save()
        self.assertFalse(notification.is_read)

    def test_notification_str(self):
        """
        Test the string representation of the notification.
        """

        self.assertEqual(
            str(self.notification), f"Notification for {self.user.username}"
        )

    def test_notification_message_help_text(self):
        """
        Test the help text for the notification message field.
        """

        field_help_text = self.notification._meta.get_field("message").help_text
        self.assertEqual(field_help_text, "Notification message")
