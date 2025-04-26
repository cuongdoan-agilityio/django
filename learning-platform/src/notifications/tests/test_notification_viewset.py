from uuid import uuid4
from core.tests.base import BaseTestCase
from rest_framework import status

from notifications.factories import NotificationFactory
from notifications.models import Notification


class NotificationViewSetTestCase(BaseTestCase):
    """
    Test case for the NotificationViewSet.

    This test cases covers the functionality of the NotificationViewSet,
    including listing, retrieving, and updating notifications.
    """

    def setUp(self):
        super().setUp()
        self.url_list = f"{self.root_url}notifications/"

        self.first_notification = NotificationFactory(user=self.user, is_read=False)
        self.more_notification = NotificationFactory(user=self.user, is_read=True)
        self.instructor_user_notification = NotificationFactory(
            user=self.instructor_user, is_read=False
        )

    def test_list_notifications(self):
        """
        Test that the list of notifications is returned correctly.
        """
        response = self.get_json(
            url=self.url_list,
            email=self.user,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data.get("data")
        response_pagination = response.data.get("meta").get("pagination")
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_pagination["total"], 2)
        self.assertEqual(response_pagination["limit"], 20)
        self.assertEqual(response_pagination["offset"], 0)
        self.assertIn(str(self.first_notification.id), [n["id"] for n in response_data])
        self.assertIn(str(self.more_notification.id), [n["id"] for n in response_data])

    def test_get_empty_notifications(self):
        """
        Test that an empty list is returned when there are no notifications.
        """

        Notification.objects.all().delete()

        response = self.get_json(
            url=self.url_list,
            email=self.user,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data.get("data")
        response_pagination = response.data.get("meta").get("pagination")
        self.assertEqual(len(response_data), 0)
        self.assertEqual(response_pagination["total"], 0)
        self.assertEqual(response_pagination["limit"], 20)
        self.assertEqual(response_pagination["offset"], 0)

    def test_get_notification_without_authentication(self):
        """
        Test that an authentication error is returned when trying to get notifications without authentication.
        """

        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_notification_with_invalid_http_method(self):
        """
        Test that an error is returned when using an invalid HTTP method.
        """

        response = self.post_json(url=self.url_list, data=None, email=self.user)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_other_user_notifications(self):
        """
        Test that a user cannot access notifications belonging to another user.
        """
        response = self.get_json(
            url=self.url_list,
            email=self.user,
        )
        self.assertNotIn(
            str(self.instructor_user_notification.id),
            [n["id"] for n in response.data.get("data")],
        )

    def test_retrieve_notification(self):
        """
        Test that a single notification is retrieved correctly.
        """

        response = self.get_json(
            url=f"{self.url_list}{str(self.first_notification.id)}/",
            email=self.user,
        )

        response_data = response.data.get("data")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["id"], str(self.first_notification.id))
        self.assertEqual(response_data["is_read"], self.first_notification.is_read)
        self.assertEqual(response_data["message"], self.first_notification.message)

    def test_retrieve_notification_without_authentication(self):
        """
        Test that an authentication error is returned when trying to retrieve a notification without authentication.
        """

        response = self.client.get(f"{self.url_list}{str(self.first_notification.id)}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_notification_of_another_user(self):
        """
        Test that an error is returned when trying to retrieve a notification of another user.
        """

        response = self.get_json(
            url=f"{self.url_list}{str(self.instructor_user_notification.id)}/",
            email=self.user,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_notification_with_invalid_notification_id(self):
        """
        Test that an error is returned when trying to retrieve a notification with an invalid ID.
        """

        response = self.get_json(
            url=f"{self.url_list}{str(uuid4())}/",
            email=self.user,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_notification_with_invalid_http_method(self):
        """
        Test that an error is returned when using an invalid HTTP method.
        """

        response = self.post_json(
            url=f"{self.url_list}{str(self.first_notification.id)}/",
            data=None,
            email=self.user,
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_notification(self):
        """
        Test that a notification is partially updated correctly.
        """
        pass

    def test_partial_update_notification_without_authentication(self):
        """
        Test that an authentication error is returned when trying to partially update a notification without authentication.
        """
        pass

    def test_partial_update_notification_of_another_user(self):
        """
        Test that an error is returned when trying to partially update a notification of another user.
        """
        pass

    def test_partial_update_notification_with_invalid_notification_id(self):
        """
        Test that an error is returned when trying to partially update a notification with an invalid ID.
        """
        pass

    def test_partial_update_notification_with_invalid_http_method(self):
        """
        Test that an error is returned when using an invalid HTTP method.
        """
        pass

    def test_partial_update_notification_with_invalid_data(self):
        """
        Test that an error is returned when trying to partially update a notification with invalid data.
        """
        pass
