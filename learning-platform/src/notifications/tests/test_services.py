from notifications.services import NotificationServices
from notifications.models import Notification
from core.test import BaseAPITestCase


class TestHandlePartialUpdate(BaseAPITestCase):
    """
    Unit tests for the handle_partial_update method in NotificationServices.
    """

    def test_handle_partial_update_success(self, fake_notification):
        """
        Test that the `is_read` field of a notification is successfully updated.
        """

        data = {"is_read": True}
        updated_notification = NotificationServices().handle_partial_update(
            fake_notification, data
        )

        assert updated_notification.is_read is True
        assert Notification.objects.get(id=fake_notification.id).is_read is True

    def test_handle_partial_update_no_changes(self, fake_notification):
        """
        Test that the notification remains unchanged when no valid fields are provided.
        """

        data = {}
        is_read = fake_notification.is_read
        updated_notification = NotificationServices().handle_partial_update(
            fake_notification, data
        )

        assert updated_notification.is_read == is_read

    def test_handle_partial_update_invalid_field(self, fake_notification):
        """
        Test that invalid fields in the data do not affect the notification.
        """

        data = {"invalid_field": "invalid_value"}
        is_read = fake_notification.is_read
        updated_notification = NotificationServices().handle_partial_update(
            fake_notification, data
        )

        assert updated_notification.is_read is is_read
