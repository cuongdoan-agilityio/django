import uuid
from django.core.signing import SignatureExpired
from rest_framework import status
from unittest.mock import patch

from core.tests.base import BaseTestCase
from core.error_messages import ErrorMessage
from core.helpers import create_token


class UserViewSetTests(BaseTestCase):
    """
    Unit tests for the UserViewSet class.
    """

    def setUp(self):
        """
        Set up the test data.
        """

        super().setUp()

        self.retrieve_url = f"{self.root_url}users/me/"
        self.verify_change_password_url = (
            f"{self.root_url}users/verify-change-password/"
        )
        self.change_password_url = f"{self.root_url}users/change-password/"
        self.new_password = "NewPassword@123"
        self.password_token = create_token(self.user.email)

    def test_retrieve_student_profile(self):
        """
        Test the retrieve action for a student.
        """

        response = self.get_json(url=self.retrieve_url, email=self.email)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_instructor_profile(self):
        """
        Test the retrieve action for an instructor.
        """

        response = self.get_json(url=self.retrieve_url, email=self.instructor_email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_student_profile(self):
        """
        Test the partial_update action for a student.
        """

        data = {
            "phone_number": self.random_user_phone_number(),
            "scholarship": self.random_scholarship(),
            "date_of_birth": self.random_date_of_birth(is_student=True),
        }

        response = self.patch_json(
            url=f"{self.root_url}users/{self.student_user.id}/",
            email=self.email,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_student_profile_with_invalid_email(self):
        """
        Test the partial_update action for a student with invalid email.
        """

        data = {
            "phone_number": self.random_user_phone_number(),
            "scholarship": self.random_scholarship(),
            "date_of_birth": "1910-01-01",
        }

        response = self.patch_json(
            url=f"{self.root_url}users/{self.student_user.id}/",
            email=self.email,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_instructor_profile(self):
        """
        Test the partial_update action for an instructor.
        """

        data = {
            "phone_number": self.random_user_phone_number(),
            "degree": self.random_degree(),
            "date_of_birth": self.random_date_of_birth(is_student=False),
            "specializations": [self.specialization.id],
        }

        response = self.patch_json(
            url=f"{self.root_url}users/{self.instructor_user.id}/",
            email=self.instructor_email,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_instructor_profile_with_invalid_specializations(self):
        """
        Test the partial_update action for an instructor with invalid specialization.
        """

        data = {
            "phone_number": self.random_user_phone_number(),
            "degree": self.random_degree(),
            "date_of_birth": self.random_date_of_birth(is_student=False),
            "specializations": [str(uuid.uuid4())],
        }

        response = self.patch_json(
            url=f"{self.root_url}users/{self.instructor_user.id}/",
            email=self.instructor_email,
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_instructor_profile_forbidden(self):
        """
        Test the partial_update action for an instructor with forbidden.
        """

        data = {"specializations": [str(uuid.uuid4())]}

        response = self.patch_json(
            url=f"{self.root_url}users/{str(uuid.uuid4())}/",
            email=self.instructor_email,
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("accounts.tasks.send_password_reset_email.delay")
    def test_verify_change_password_success(self, mock_send_password_reset_email):
        """
        Test verifying change password with a valid token.
        """

        data = {"password": self.new_password}

        response = self.post_json(
            self.verify_change_password_url, data, email=self.user.email
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_password_reset_email.assert_called_once()

    def test_verify_change_password_missing_token(self):
        """
        Test verifying change password with a missing token.
        """
        data = {}
        response = self.post_json(
            self.verify_change_password_url, data, email=self.user.email
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"password": ["This field is required."]})

    def test_verify_change_password_invalid_data(self):
        """
        Test verifying change password with an invalid data.
        """
        data = {"password": "InvalidPassword"}
        response = self.post_json(
            self.verify_change_password_url, data, email=self.user.email
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"password": [ErrorMessage.PASSWORD_NUMBER]})

    @patch("accounts.tasks.send_password_reset_email.delay")
    def test_verify_change_password_email_sending_failure(
        self, mock_send_password_reset_email
    ):
        """
        Test verifying change password when email sending fails.
        """
        mock_send_password_reset_email.side_effect = Exception("Email sending failed")
        data = {"password": self.new_password}

        response = self.post_json(
            self.verify_change_password_url, data, email=self.user.email
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_change_password_invalid_http_method(self):
        """
        Test verifying change password with invalid HTTP methods.
        """

        data = {"password": self.new_password}
        response = self.patch_json(
            self.verify_change_password_url, data, email=self.user.email
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_change_password_success(self):
        """
        Test changing password with a valid token.
        """

        data = {"token": self.password_token}
        response = self.post_json(self.change_password_url, data, email=self.user.email)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_missing_token(self):
        """
        Test changing password with a missing token.
        """

        response = self.post_json(
            self.change_password_url, data={}, email=self.user.email
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"token": [ErrorMessage.REQUIRED_FIELD]})

    def test_change_password_invalid_token(self):
        """
        Test changing password with an invalid token.
        """
        data = {"token": "InvalidToken"}
        response = self.post_json(
            self.change_password_url, data=data, email=self.user.email
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_expired_token(self):
        """
        Test changing password with an expired token.
        """

        with patch("django.core.signing.TimestampSigner.unsign") as mock_unsign:
            mock_unsign.side_effect = SignatureExpired("Token has expired")
            data = {"token": self.password_token}
            response = self.post_json(
                self.change_password_url, data, email=self.user.email
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_invalid_http_method(self):
        """
        Test changing password with invalid HTTP methods.
        """

        response = self.get_json(self.change_password_url, email=self.user.email)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        data = {"token": self.password_token}
        response = self.patch_json(
            self.change_password_url, data=data, email=self.user.email
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_change_password_unauthenticated(self):
        """
        Test changing password without authentication.
        """
        data = {"token": self.password_token}

        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
