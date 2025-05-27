import pytest
from uuid import uuid4
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.signing import SignatureExpired
from rest_framework import status
from unittest.mock import patch
from core.error_messages import ErrorMessage
from core.helpers import create_token


@pytest.mark.django_db
class TestAuthorViewSet:
    """
    Test suite for the AuthorViewSet.
    """

    def test_login_success(
        self,
        api_client,
        login_url,
        fake_instructor,
    ):
        """
        Test login success.
        """

        data = {"email": fake_instructor.email, "password": "Password@123"}
        response = api_client.post(login_url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_login_failure(
        self,
        api_client,
        login_url,
        fake_student,
    ):
        """
        Test login failure with invalid password.
        """

        data = {"email": fake_student.email, "password": "wrong_password"}
        response = api_client.post(login_url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_failure_with_inactivate_user(
        self,
        api_client,
        login_url,
        fake_new_user,
    ):
        """
        Test login failure with invalid password.
        """

        data = {"email": fake_new_user.email, "password": "Password@123"}
        response = api_client.post(login_url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("errors")["field"] == "email"
        assert response.data.get("errors")["message"][0] == ErrorMessage.USER_NOT_ACTIVE

    def test_signup(
        self, api_client, signup_url, faker, random_gender, random_scholarship
    ):
        """
        Test the signup action.
        """

        data = {
            "username": faker.user_name(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(),
            "password": "Newpassword@123",
            "phone_number": faker.phone_number(),
            "date_of_birth": "2000-01-01",
            "gender": random_gender,
            "scholarship": random_scholarship,
        }
        response = api_client.post(signup_url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"data": {"success": True}}

    def test_signup_with_invalid_username(
        self,
        fake_instructor,
        faker,
        signup_url,
        api_client,
    ):
        """
        Test the signup action with invalid user name.
        """

        data = {
            "username": fake_instructor.username,
            "email": faker.email(),
            "password": "Password@123",
        }
        response = api_client.post(signup_url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_with_invalid_email(
        self,
        api_client,
        signup_url,
        faker,
        fake_student,
    ):
        """
        Test the signup action with an invalid email.
        """

        data = {
            "username": faker.user_name(),
            "email": fake_student.email,
            "password": "password123",
        }
        response = api_client.post(signup_url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("accounts.tasks.send_welcome_email.delay")
    def test_verify_email_success(
        self,
        mock_send_welcome_email,
        api_client,
        verify_url,
        fake_new_user,
    ):
        """
        Test verifying email with a valid token.
        """

        token = create_token(fake_new_user.id)
        response = api_client.post(
            f"{verify_url}",
            data={"token": token},
        )
        assert response.status_code == status.HTTP_200_OK

        fake_new_user.refresh_from_db()
        assert fake_new_user.is_active

        mock_send_welcome_email.assert_called_once_with(
            {"username": fake_new_user.username, "email": fake_new_user.email}
        )

    def test_verify_email_invalid_token(
        self,
        api_client,
        verify_url,
    ):
        """
        Test verifying email with an invalid token.
        """

        response = api_client.post(f"{verify_url}", data={"token": "invalid_token"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response.data

    def test_verify_email_expired_token(
        self,
        api_client,
        verify_url,
        fake_new_user,
    ):
        """
        Test verifying email with an expired token.
        """

        token = create_token(fake_new_user.id)

        with patch("django.core.signing.TimestampSigner.unsign") as mock_unsign:
            mock_unsign.side_effect = SignatureExpired("Token has expired")
            response = api_client.post(f"{verify_url}", data={"token": token})

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "errors" in response.data

    def test_verify_email_nonexistent_user(
        self,
        signer,
        api_client,
        verify_url,
    ):
        """
        Test verifying email for a nonexistent user.
        """

        value = str(uuid4())
        signed_value = signer.sign(value)
        token = urlsafe_base64_encode(force_bytes(signed_value))

        response = api_client.post(f"{verify_url}", data={"token": token})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response.data

    @patch("accounts.tasks.send_welcome_email.delay")
    def test_verify_email_user_already_active(
        self,
        mock_send_welcome_email,
        api_client,
        verify_url,
        fake_new_user,
    ):
        """
        Test verifying email for a user who is already active.
        """

        fake_new_user.is_active = True
        fake_new_user.save()
        token = create_token(fake_new_user.id)

        response = api_client.post(
            f"{verify_url}",
            data={"token": token},
        )

        fake_new_user.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert fake_new_user.is_active
        mock_send_welcome_email.assert_not_called()

    @patch("accounts.tasks.send_password_reset_email.delay")
    def test_reset_password_success(
        self,
        mock_send_password_reset_email,
        api_client,
        reset_password_url,
        reset_password_data,
    ):
        """
        Test verifying reset password with a valid token.
        """

        response = api_client.post(
            reset_password_url,
            reset_password_data,
        )

        assert response.status_code == status.HTTP_200_OK
        mock_send_password_reset_email.assert_called_once()

    def test_reset_password_missing_email(
        self,
        api_client,
        reset_password_url,
    ):
        """
        Test verifying reset password with a missing email.
        """

        data = {}
        response = api_client.post(
            reset_password_url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("errors")[0]["field"] == "email"
        assert response.data.get("errors")[0]["message"][0] == "This field is required."

    def test_reset_password_invalid_data(
        self,
        api_client,
        reset_password_url,
    ):
        """
        Test verifying reset password with an invalid data.
        """

        data = {"email": "InvalidEmail"}
        response = api_client.post(
            reset_password_url,
            data,
            format="json",
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
        api_client,
        reset_password_url,
        reset_password_data,
    ):
        """
        Test verifying reset password when email sending fails.
        """

        mock_send_password_reset_email.side_effect = Exception("Email sending failed")

        response = api_client.post(
            reset_password_url,
            reset_password_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_invalid_http_method(
        self,
        api_client,
        reset_password_url,
        reset_password_data,
    ):
        """
        Test verifying reset password with invalid HTTP methods.
        """

        response = api_client.patch(
            reset_password_url,
            reset_password_data,
            format="json",
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_reset_password_with_not_found_user(
        self,
        api_client,
        faker,
        reset_password_url,
    ):
        """
        Test verifying reset password with user not found.
        """

        data = {"email": faker.email()}

        response = api_client.post(
            reset_password_url,
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_password_success(
        self,
        api_client,
        confirm_reset_password_url,
        fake_new_user,
    ):
        """
        Test reset password with a valid token.
        """

        token = create_token(fake_new_user.email)

        response = api_client.post(
            f"{confirm_reset_password_url}",
            data={"token": token, "password": "Password@123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("data") == {"success": True}

    def test_confirm_reset_password_missing_password_and_token(
        self,
        api_client,
        confirm_reset_password_url,
    ):
        """
        Test changing password with a missing token.
        """

        response = api_client.post(f"{confirm_reset_password_url}", data={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get("errors")[0]["field"] == "token"
        assert response.data.get("errors")[1]["field"] == "password"
        assert response.data.get("errors")[0]["message"][0] == "This field is required."
        assert response.data.get("errors")[1]["message"][0] == "This field is required."

    def test_confirm_reset_password_invalid_token(
        self, api_client, confirm_reset_password_url
    ):
        """
        Test reset password with an invalid token.
        """

        response = api_client.post(
            f"{confirm_reset_password_url}",
            data={"token": "InvalidToken", "password": "Password@123"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_password_expired_token(
        self,
        api_client,
        confirm_reset_password_url,
        fake_new_user,
    ):
        """
        Test reset password with an expired token.
        """

        token = create_token(fake_new_user.email)

        with patch("django.core.signing.TimestampSigner.unsign") as mock_unsign:
            mock_unsign.side_effect = SignatureExpired("Token has expired")
            response = api_client.post(
                f"{confirm_reset_password_url}",
                data={"token": token, "password": "Password@123"},
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_reset_password_invalid_http_method(
        self,
        api_client,
        confirm_reset_password_url,
        fake_new_user,
    ):
        """
        Test reset password with invalid HTTP methods.
        """

        token = create_token(fake_new_user.email)

        response = api_client.get(
            f"{confirm_reset_password_url}",
            format="json",
        )

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        data = {"token": token}
        response = api_client.patch(
            f"{confirm_reset_password_url}",
            data=data,
            format="json",
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
