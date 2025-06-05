import pytest
from uuid import uuid4
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.signing import SignatureExpired, TimestampSigner
from rest_framework import status
from unittest.mock import patch
from core.error_messages import ErrorMessage
from core.helpers import create_token
from .base import BaseAccountModuleTestCase


class TestAuthorViewSet(BaseAccountModuleTestCase):
    """
    Test suite for the AuthorViewSet.
    """

    fragment = "auth/"

    @pytest.fixture(autouse=True)
    def init_data(self, setup):
        """
        Initialize data for the test cases.
        """

        self.auth = None
        self.reset_password_data = {"email": self.fake_other_student.email}
        self.fake_other_student.is_active = False
        self.fake_other_student.save()

    def test_login_success(self):
        """
        Test login success.
        """

        data = {"email": self.fake_instructor.email, "password": "Password@123"}
        response = self.post_json(fragment=f"{self.fragment}login/", data=data)

        assert response.status_code == status.HTTP_200_OK

    def test_login_failure(self):
        """
        Test login failure with invalid password.
        """

        data = {"email": self.fake_student.email, "password": "wrong_password"}
        response = self.post_json(fragment=f"{self.fragment}login/", data=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_failure_with_inactivate_user(self):
        """
        Test login failure with invalid password.
        """

        data = {"email": self.fake_other_student.email, "password": "Password@123"}
        response = self.post_json(fragment=f"{self.fragment}login/", data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("errors")["field"] == "email"
        assert response.data.get("errors")["message"][0] == ErrorMessage.USER_NOT_ACTIVE

    def test_signup(self):
        """
        Test the signup action.
        """

        data = {
            "username": self.faker.user_name(),
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "email": self.faker.email(),
            "password": "Newpassword@123",
            "phone_number": self.faker.phone_number(),
            "date_of_birth": "2000-01-01",
            "gender": self.random_gender,
            "scholarship": self.random_scholarship,
        }
        response = self.post_json(fragment=f"{self.fragment}signup/", data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"data": {"success": True}}

    def test_signup_with_invalid_username(self):
        """
        Test the signup action with invalid user name.
        """

        data = {
            "username": self.fake_instructor.username,
            "email": self.faker.email(),
            "password": "Password@123",
        }
        response = self.post_json(fragment=f"{self.fragment}signup/", data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_with_invalid_email(self):
        """
        Test the signup action with an invalid email.
        """

        data = {
            "username": self.faker.user_name(),
            "email": self.fake_student.email,
            "password": "password123",
        }
        response = self.post_json(fragment=f"{self.fragment}signup/", data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("accounts.tasks.send_welcome_email.delay")
    def test_verify_email_success(
        self,
        mock_send_welcome_email,
    ):
        """
        Test verifying email with a valid token.
        """

        token = create_token(self.fake_other_student.id)
        response = self.post_json(
            f"{self.fragment}confirm-signup-email/",
            data={"token": token},
        )
        self.fake_other_student.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert self.fake_other_student.is_active

        mock_send_welcome_email.assert_called_once_with(
            {
                "username": self.fake_other_student.username,
                "email": self.fake_other_student.email,
            }
        )

    def test_verify_email_invalid_token(self):
        """
        Test verifying email with an invalid token.
        """

        response = self.post_json(
            fragment=f"{self.fragment}confirm-signup-email/",
            data={"token": "invalid_token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response.data

    def test_verify_email_expired_token(self):
        """
        Test verifying email with an expired token.
        """

        token = create_token(self.fake_other_student.id)

        with patch("django.core.signing.TimestampSigner.unsign") as mock_unsign:
            mock_unsign.side_effect = SignatureExpired("Token has expired")
            response = self.post_json(
                f"{self.fragment}confirm-signup-email/", data={"token": token}
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "errors" in response.data

    def test_verify_email_nonexistent_user(self):
        """
        Test verifying email for a nonexistent user.
        """

        signer = TimestampSigner()
        value = str(uuid4())
        signed_value = signer.sign(value)
        token = urlsafe_base64_encode(force_bytes(signed_value))
        response = self.post_json(
            f"{self.fragment}confirm-signup-email/", data={"token": token}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response.data

    @patch("accounts.tasks.send_welcome_email.delay")
    def test_verify_email_user_already_active(
        self,
        mock_send_welcome_email,
    ):
        """
        Test verifying email for a user who is already active.
        """

        self.fake_other_student.is_active = True
        self.fake_other_student.save()
        token = create_token(self.fake_other_student.id)
        response = self.post_json(
            f"{self.fragment}confirm-signup-email/",
            data={"token": token},
        )
        self.fake_other_student.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert self.fake_other_student.is_active
        mock_send_welcome_email.assert_not_called()

    @patch("accounts.tasks.send_password_reset_email.delay")
    def test_reset_password_success(
        self,
        mock_send_password_reset_email,
    ):
        """
        Test verifying reset password with a valid token.
        """

        response = self.post_json(
            f"{self.fragment}reset-password/",
            self.reset_password_data,
        )

        assert response.status_code == status.HTTP_200_OK
        mock_send_password_reset_email.assert_called_once()

    def test_reset_password_missing_email(self):
        """
        Test verifying reset password with a missing email.
        """

        data = {}
        response = self.post_json(
            f"{self.fragment}reset-password/",
            data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("errors")[0]["field"] == "email"
        assert response.data.get("errors")[0]["message"][0] == "This field is required."

    def test_reset_password_invalid_data(self):
        """
        Test verifying reset password with an invalid data.
        """

        data = {"email": "InvalidEmail"}
        response = self.post_json(
            f"{self.fragment}reset-password/",
            data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("errors")[0]["field"] == "email"
        assert (
            response.data.get("errors")[0]["message"][0]
            == "Enter a valid email address."
        )

    @patch("accounts.tasks.send_password_reset_email.delay")
    def test_reset_password_email_sending_failure(
        self,
        mock_send_password_reset_email,
    ):
        """
        Test verifying reset password when email sending fails.
        """

        mock_send_password_reset_email.side_effect = Exception("Email sending failed")

        response = self.post_json(
            f"{self.fragment}reset-password/",
            self.reset_password_data,
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_reset_password_invalid_http_method(self):
        """
        Test verifying reset password with invalid HTTP methods.
        """

        response = self.patch_json(
            f"{self.fragment}reset-password/",
            self.reset_password_data,
        )

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_reset_password_with_not_found_user(self):
        """
        Test verifying reset password with user not found.
        """

        data = {"email": self.faker.email()}
        response = self.post_json(
            f"{self.fragment}reset-password/",
            data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_password_success(self):
        """
        Test reset password with a valid token.
        """

        token = create_token(self.fake_other_student.email)
        response = self.post_json(
            f"{self.fragment}confirm-reset-password/",
            data={"token": token, "password": "Password@123"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("data") == {"success": True}

    def test_confirm_reset_password_missing_password_and_token(self):
        """
        Test changing password with a missing token.
        """

        response = self.post_json(f"{self.fragment}confirm-reset-password/", data={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("errors")[0]["field"] == "token"
        assert response.data.get("errors")[1]["field"] == "password"
        assert response.data.get("errors")[0]["message"][0] == "This field is required."
        assert response.data.get("errors")[1]["message"][0] == "This field is required."

    def test_confirm_reset_password_invalid_token(self):
        """
        Test reset password with an invalid token.
        """

        response = self.post_json(
            f"{self.fragment}confirm-reset-password/",
            data={"token": "InvalidToken", "password": "Password@123"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_password_expired_token(self):
        """
        Test reset password with an expired token.
        """

        token = create_token(self.fake_other_student.email)

        with patch("django.core.signing.TimestampSigner.unsign") as mock_unsign:
            mock_unsign.side_effect = SignatureExpired("Token has expired")
            response = self.post_json(
                f"{self.fragment}confirm-reset-password/",
                data={"token": token, "password": "Password@123"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_password_invalid_http_method(self):
        """
        Test reset password with invalid HTTP methods.
        """

        token = create_token(self.fake_other_student.email)
        response = self.get_json(f"{self.fragment}confirm-reset-password/")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        data = {"token": token}
        response = self.patch_json(
            f"{self.fragment}confirm-reset-password/",
            data=data,
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
