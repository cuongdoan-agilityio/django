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
        self.verify_url = f"{self.root_url}auth/verify-email/"

        self.new_user = UserFactory(
            is_active=False,
        )
        self.signer = TimestampSigner()
        self.token = create_token(self.new_user.id)

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
        self.assertEqual(response.data, {"success": True})

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

        response = self.client.post(
            self.verify_url, {"token": self.token}, format="json"
        )

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
        response = self.client.post(
            self.verify_url, {"token": "invalid_token"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)

    def test_verify_email_expired_token(self):
        """
        Test verifying email with an expired token.
        """

        # Simulate an expired token by using a past timestamp
        with patch("django.core.signing.TimestampSigner.unsign") as mock_unsign:
            mock_unsign.side_effect = SignatureExpired("Token has expired")

            response = self.client.post(
                self.verify_url, {"token": self.token}, format="json"
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("errors", response.data)

    def test_verify_email_nonexistent_user(self):
        """
        Test verifying email for a nonexistent user.
        """

        value = str(uuid4())
        signed_value = self.signer.sign(value)
        token = urlsafe_base64_encode(force_bytes(signed_value))

        response = self.client.post(self.verify_url, {"token": token}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)

    @patch("accounts.tasks.send_welcome_email.delay")
    def test_verify_email_user_already_active(self, mock_send_welcome_email):
        """
        Test verifying email for a user who is already active.
        """

        self.new_user.is_active = True
        self.new_user.save()

        response = self.client.post(
            self.verify_url, {"token": self.token}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        mock_send_welcome_email.assert_not_called()
