from unittest.mock import patch
from django.conf import settings
from sendgrid import SendGridAPIClient

from accounts.tasks import send_welcome_email, send_password_reset_email
from core.constants import URL


class TestSendWelcomeEmail:
    """
    Unit tests for the send_welcome_email Celery task.
    """

    @patch("accounts.tasks.send_email")
    def test_send_welcome_email_success(self, mock_send_email, user_data):
        """
        Test that the send_welcome_email task successfully sends an email.
        """

        mock_send_email.return_value = None

        send_welcome_email(user_data)

        mock_send_email.assert_called_once_with(
            user_data["email"],
            {
                "user_name": user_data["username"],
                "sender_name": settings.SENDER_NAME,
                "subject": "Welcome to Our Platform",
            },
            settings.WELCOME_TEMPLATE_ID,
        )

    @patch.object(SendGridAPIClient, "send")
    def test_send_welcome_email_success_call_sendgrid(self, mock_send, user_data):
        """
        Test that the send_welcome_email task successfully calls SendGridAPIClient.send.
        """

        send_welcome_email(user_data)
        mock_send.assert_called_once()

    @patch("core.helpers.send_capture_message")
    @patch.object(SendGridAPIClient, "send")
    def test_send_welcome_email_failure(
        self, mock_send, mock_send_capture_message, user_data
    ):
        """
        Test that the send_welcome_email task handles email sending failure.
        """

        mock_send.side_effect = Exception("Email sending failed")
        send_welcome_email(user_data)
        mock_send_capture_message.assert_called_once()


class TestSendPasswordResetEmail:
    """
    Unit tests for the send_password_reset_email Celery task.
    """

    @patch("accounts.tasks.send_email")
    def test_send_password_reset_email_success(self, mock_send_email, reset_email_data):
        """
        Test that the send_password_reset_email task sends an email successfully.
        """

        mock_send_email.return_value = None
        send_password_reset_email(reset_email_data, reset_email_data["token"])

        mock_send_email.assert_called_once_with(
            reset_email_data["email"],
            {
                "user_name": reset_email_data["username"],
                "sender_name": settings.SENDER_NAME,
                "subject": "Verify Password Change",
                "activation_link": f"{settings.APP_DOMAIN}/{URL['RESET_PASSWORD']}/?token={reset_email_data['token']}",
            },
            settings.VERIFY_RESET_PASSWORD_TEMPLATE_ID,
        )

    @patch("core.helpers.send_capture_message")
    @patch.object(SendGridAPIClient, "send")
    def test_send_password_reset_email_failure(
        self, mock_send, mock_send_capture_message, reset_email_data
    ):
        """
        Test that the send_password_reset_email task handles email sending failure.
        """

        mock_send.side_effect = Exception("Email sending failed")
        send_password_reset_email(reset_email_data, reset_email_data["token"])
        mock_send_capture_message.assert_called_once()

    @patch.object(SendGridAPIClient, "send")
    def test_send_password_reset_email_success_call_sendgrid(
        self, mock_send, reset_email_data
    ):
        """
        Test that the send_password_reset_email task successfully calls SendGridAPIClient.send.
        """

        send_password_reset_email(reset_email_data, reset_email_data["token"])
        mock_send.assert_called_once()
