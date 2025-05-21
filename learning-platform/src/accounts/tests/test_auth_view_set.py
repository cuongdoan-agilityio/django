from uuid import uuid4
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.signing import TimestampSigner, SignatureExpired
from rest_framework import status
from unittest.mock import patch

from accounts.factories import UserFactory
from core.tests.base import BaseTestCase
from core.helpers import create_token


class AuthorViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.login_url = f"{self.root_url}auth/login/"
        self.signup = f"{self.root_url}auth/signup/"
        self.verify_url = f"{self.root_url}auth/confirm-signup-email/"

        self.verify_reset_password_url = f"{self.root_url}auth/confirm-reset-password/"
        self.reset_password_url = f"{self.root_url}auth/reset-password/"
        self.new_password = "NewPassword@123"
        self.email_token = create_token(self.user.email)

        self.new_user = UserFactory(
            is_active=False,
        )
        self.signer = TimestampSigner()
        self.token = create_token(self.new_user.id)

        self.verify_reset_password_data = {"email": self.new_user.email}
        self.reset_password_data = {"token": self.email_token}

    def test_login_success(self):
        """
        Test login success.
        """

        data = {
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_failure(self):
        """
        Test login invalid with invalid password.
        """

        data = {"email": self.email, "password": "wrong_password"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_signup(self):
        """
        Test the signup action.
        """

        data = {
            "username": self.fake.user_name(),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "email": self.fake.email(),
            "password": "Newpassword@123",
            "phone_number": self.random_user_phone_number(),
            "date_of_birth": self.random_date_of_birth(is_student=True),
            "gender": self.random_gender(),
            "scholarship": self.random_scholarship(),
        }
        response = self.client.post(self.signup, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"data": {"success": True}})

    def test_signup_with_invalid_username(self):
        """
        Test the signup action with invalid user name.
        """

        data = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(self.signup, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_invalid_email(self):
        """
        Test the signup action with invalid email.
        """

        data = {
            "username": self.fake.user_name(),
            "email": self.email,
            "password": self.password,
        }
        response = self.client.post(self.signup, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("accounts.tasks.send_welcome_email.delay")
    def test_verify_email_success(self, mock_send_welcome_email):
        """
        Test verifying email with a valid token.
        """

        response = self.client.get(f"{self.verify_url}?token={self.token}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

        mock_send_welcome_email.assert_called_once_with(
            {"username": self.new_user.username, "email": self.new_user.email}
        )

    def test_verify_email_invalid_token(self):
        """
        Test verifying email with an invalid token.
        """
        response = self.client.get(f"{self.verify_url}?token=invalid_token")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)

    def test_verify_email_expired_token(self):
        """
        Test verifying email with an expired token.
        """

        # Simulate an expired token by using a past timestamp
        with patch("django.core.signing.TimestampSigner.unsign") as mock_unsign:
            mock_unsign.side_effect = SignatureExpired("Token has expired")

            response = self.client.get(f"{self.verify_url}?token={self.token}")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("errors", response.data)

    def test_verify_email_nonexistent_user(self):
        """
        Test verifying email for a nonexistent user.
        """

        value = str(uuid4())
        signed_value = self.signer.sign(value)
        token = urlsafe_base64_encode(force_bytes(signed_value))

        response = self.client.get(f"{self.verify_url}?token={token}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)

    @patch("accounts.tasks.send_welcome_email.delay")
    def test_verify_email_user_already_active(self, mock_send_welcome_email):
        """
        Test verifying email for a user who is already active.
        """

        self.new_user.is_active = True
        self.new_user.save()

        response = self.client.get(f"{self.verify_url}?token={self.token}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        mock_send_welcome_email.assert_not_called()

    @patch("accounts.tasks.send_password_reset_email.delay")
    def test_verify_reset_password_success(self, mock_send_password_reset_email):
        """
        Test verifying reset password with a valid token.
        """

        response = self.client.post(
            self.verify_reset_password_url,
            self.verify_reset_password_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_password_reset_email.assert_called_once()

    def test_verify_reset_password_missing_email(self):
        """
        Test verifying reset password with a missing email.
        """
        data = {}
        response = self.client.post(
            self.verify_reset_password_url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("errors")[0]["field"], "email")
        self.assertEqual(
            response.data.get("errors")[0]["message"][0], "This field is required."
        )

    def test_verify_reset_password_invalid_data(self):
        """
        Test verifying reset password with an invalid data.
        """
        data = {"email": "InvalidEmail"}
        response = self.client.post(
            self.verify_reset_password_url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("errors")[0]["field"], "email")
        self.assertEqual(
            response.data.get("errors")[0]["message"][0], "Enter a valid email address."
        )

    @patch("accounts.tasks.send_password_reset_email.delay")
    def test_verify_reset_password_email_sending_failure(
        self, mock_send_password_reset_email
    ):
        """
        Test verifying reset password when email sending fails.
        """
        mock_send_password_reset_email.side_effect = Exception("Email sending failed")

        response = self.client.post(
            self.verify_reset_password_url,
            self.verify_reset_password_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_reset_password_invalid_http_method(self):
        """
        Test verifying reset password with invalid HTTP methods.
        """

        response = self.client.patch(
            self.verify_reset_password_url,
            self.verify_reset_password_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_reset_password_success(self):
        """
        Test reset password with a valid token.
        """

        response = self.client.get(
            f"{self.reset_password_url}?token={self.reset_password_data.get('token')}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("data"), {"password": "Password@123"})

    def test_reset_password_missing_token(self):
        """
        Test changing password with a missing token.
        """

        response = self.client.get(
            f"{self.reset_password_url}?token=",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("errors")[0]["field"], "token")
        self.assertEqual(
            response.data.get("errors")[0]["message"][0], "This field may not be blank."
        )

    def test_reset_password_invalid_token(self):
        """
        Test changing password with an invalid token.
        """

        response = self.client.get(
            f"{self.reset_password_url}?token=InvalidToken",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_expired_token(self):
        """
        Test reset password with an expired token.
        """

        with patch("django.core.signing.TimestampSigner.unsign") as mock_unsign:
            mock_unsign.side_effect = SignatureExpired("Token has expired")
            response = self.client.get(
                f"{self.reset_password_url}?token={self.email_token}",
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_invalid_http_method(self):
        """
        Test reset password with invalid HTTP methods.
        """

        response = self.client.post(
            f"{self.reset_password_url}?token={self.email_token}",
            data={},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        data = {"token": self.email_token}
        response = self.client.patch(
            f"{self.reset_password_url}?token={self.email_token}",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
