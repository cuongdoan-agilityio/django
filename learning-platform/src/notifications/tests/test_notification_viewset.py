from uuid import uuid4
from rest_framework import status

from notifications.models import Notification
from core.test import BaseAPITestCase


class TestNotificationViewSet(BaseAPITestCase):
    """
    Test suite for the NotificationViewSet.
    """

    fragment = "notifications/"

    def test_list_notifications(self, fake_student_notifications):
        """
        Test that the list of notifications is returned correctly.
        """

        response = self.get_json(fragment=self.fragment)
        assert response.status_code == status.HTTP_200_OK

        response_data = response.data.get("data")
        response_pagination = response.data.get("meta").get("pagination")

        assert len(response_data) == 2
        assert response_pagination["total"] == 2
        assert response_pagination["limit"] == 20
        assert response_pagination["offset"] == 0
        assert str(fake_student_notifications[0].id) in [n["id"] for n in response_data]
        assert str(fake_student_notifications[1].id) in [n["id"] for n in response_data]

    def test_get_empty_notifications(self):
        """
        Test that an empty list is returned when there are no notifications.
        """
        Notification.objects.all().delete()

        response = self.get_json(fragment=self.fragment)
        assert response.status_code == status.HTTP_200_OK

        response_data = response.data.get("data")
        response_pagination = response.data.get("meta").get("pagination")

        assert len(response_data) == 0
        assert response_pagination["total"] == 0
        assert response_pagination["limit"] == 20
        assert response_pagination["offset"] == 0

    def test_get_notification_without_authentication(self):
        """
        Test that an authentication error is returned when trying to get notifications without authentication.
        """
        self.auth = None
        response = self.get_json(fragment=self.fragment)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_notification_with_invalid_http_method(self):
        """
        Test that an error is returned when using an invalid HTTP method.
        """

        response = self.post_json(fragment=self.fragment, data=None)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_get_other_user_notifications(self, fake_instructor_notifications):
        """
        Test that a user cannot access notifications belonging to another user.
        """

        response = self.get_json(fragment=self.fragment)
        assert str(fake_instructor_notifications[0].id) not in [
            n["id"] for n in response.data.get("data")
        ]
        assert str(fake_instructor_notifications[1].id) not in [
            n["id"] for n in response.data.get("data")
        ]

    def test_retrieve_notification(
        self,
        api_client,
        authenticated_fake_student,
        notification_url,
        fake_student_notifications,
    ):
        """
        Test that a single notification is retrieved correctly.
        """
        notification = fake_student_notifications[0]
        response = api_client.get(f"{notification_url}{notification.id}/")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.data.get("data")
        assert response_data["id"] == str(notification.id)
        assert response_data["is_read"] == notification.is_read
        assert response_data["message"] == notification.message

    def test_retrieve_notification_without_authentication(
        self, api_client, notification_url, fake_student_notifications
    ):
        """
        Test that an authentication error is returned when trying to retrieve a notification without authentication.
        """
        notification = fake_student_notifications[0]
        response = api_client.get(f"{notification_url}{notification.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_notification_with_invalid_notification_id(
        self,
        api_client,
        authenticated_fake_student,
        notification_url,
    ):
        """
        Test that an error is returned when trying to retrieve a notification with an invalid ID.
        """

        response = api_client.get(
            f"{notification_url}{str(uuid4())}/",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_notification_of_another_user(
        self,
        api_client,
        authenticated_fake_student,
        notification_url,
        fake_instructor_notifications,
    ):
        """
        Test that an error is returned when trying to retrieve a notification of another user.
        """
        response = api_client.get(
            f"{notification_url}{fake_instructor_notifications[0].id}/"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_notification_with_invalid_http_method(
        self,
        api_client,
        authenticated_fake_student,
        notification_url,
        fake_student_notifications,
    ):
        """
        Test that an error is returned when using an invalid HTTP method.
        """

        response = api_client.post(
            f"{notification_url}{str(fake_student_notifications[0].id)}/",
            data=None,
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_partial_update_notification(
        self,
        api_client,
        authenticated_fake_student,
        notification_url,
        fake_student_notifications,
    ):
        """
        Test that a notification is partially updated correctly.
        """
        notification = fake_student_notifications[0]
        payload = {"is_read": True}

        response = api_client.patch(
            f"{notification_url}{notification.id}/", data=payload
        )
        assert response.status_code == status.HTTP_200_OK

        notification.refresh_from_db()
        assert notification.is_read is True

    def test_partial_update_notification_without_authentication(
        self, api_client, notification_url, fake_instructor_notifications
    ):
        """
        Test that an authentication error is returned when trying to partially update a notification without authentication.
        """
        notification = fake_instructor_notifications[0]
        payload = {"is_read": True}

        response = api_client.patch(f"{notification_url}{notification.id}/", payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_partial_update_notification_of_another_user(
        self,
        api_client,
        authenticated_fake_student,
        notification_url,
        fake_instructor_notifications,
    ):
        """
        Test that an error is returned when trying to partially update a notification of another user.
        """

        payload = {"is_read": True}
        response = api_client.patch(
            f"{notification_url}{fake_instructor_notifications[0].id}/", data=payload
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_notification_with_invalid_data(
        self,
        api_client,
        authenticated_fake_student,
        notification_url,
        fake_student_notifications,
    ):
        """
        Test that an error is returned when trying to partially update a notification with invalid data.
        """

        notification = fake_student_notifications[0]
        payload = {"is_read": "invalid_value"}

        response = api_client.patch(
            f"{notification_url}{notification.id}/", data=payload
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["errors"][0]["field"] == "is_read"
        assert response_data["errors"][0]["message"][0] == "Must be a valid boolean."

    def test_partial_update_notification_with_invalid_notification_id(
        self,
        api_client,
        authenticated_fake_student,
        notification_url,
    ):
        """
        Test that an error is returned when trying to partially update a notification with an invalid ID.
        """

        payload = {"is_read": True}
        response = api_client.patch(
            f"{notification_url}{str(uuid4())}/",
            data=payload,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_partial_update_notification_with_invalid_http_method(
        self,
        api_client,
        authenticated_fake_student,
        notification_url,
        fake_student_notifications,
    ):
        """
        Test that an error is returned when using an invalid HTTP method.
        """

        payload = {"is_read": True}
        response = api_client.put(
            f"{notification_url}{str(fake_student_notifications[1].id)}/",
            data=payload,
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
