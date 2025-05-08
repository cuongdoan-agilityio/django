from sendgrid import SendGridAPIClient
from unittest.mock import patch
from django.conf import settings
from accounts.tasks import send_welcome_email, send_password_reset_email
from core.tests.base import BaseTestCase


class SendWelcomeEmailTest(BaseTestCase):
    """
    Unit tests for the send_welcome_email Celery task.
    """

    def setUp(self):
        super().setUp()

        self.username = self.fake.user_name()
        self.email = self.fake.email()
        self.user_data = {
            "username": self.username,
            "email": self.email,
        }

    @patch("accounts.tasks.send_email")
    def test_send_welcome_email_success(self, mock_send_email):
        """
        Test that the send_welcome_email task successfully sends an email.
        """
        mock_send_email.return_value = None

        send_welcome_email(self.user_data)

        mock_send_email.assert_called_once_with(
            self.user_data["email"],
            {
                "user_name": self.user_data["username"],
                "sender_name": settings.SENDER_NAME,
                "subject": "Welcome to Our Platform",
            },
            settings.WELCOME_TEMPLATE_ID,
        )

    @patch.object(SendGridAPIClient, "send")
    def test_send_welcome_email_success_call_sendgrid(self, mock_send):
        """
        Test that the send_welcome_email task successfully sends an email.
        """

        send_welcome_email(self.user_data)

        mock_send.assert_called_once()

    @patch("core.helpers.send_capture_message")
    @patch.object(SendGridAPIClient, "send")
    def test_send_welcome_email_failure(self, mock_send, mock_send_capture_message):
        """
        Test that the send_welcome_email task handles email sending failure.
        """
        mock_send.side_effect = Exception("Email sending failed")
        send_welcome_email(self.user_data)
        mock_send_capture_message.assert_called_once()


class SendPasswordResetEmailTest(BaseTestCase):
    """
    Unit tests for the send_password_reset_email Celery task.
    """

    def setUp(self):
        """
        Set up test data for the task.
        """

        super().setUp()
        self.username = self.fake.user_name()
        self.email = self.fake.email()
        self.user_data = {
            "username": self.username,
            "email": self.email,
        }

        self.token = "mocked_token"

    @patch("accounts.tasks.send_email")
    def test_send_password_reset_email_success(self, mock_send_email):
        """
        Test that the send_password_reset_email task sends an email successfully.
        """

        mock_send_email.return_value = None

        send_password_reset_email(self.user_data, self.token)

        mock_send_email.assert_called_once_with(
            self.email,
            {
                "user_name": self.username,
                "token": self.token,
                "sender_name": settings.SENDER_NAME,
                "subject": "Verify Password Change",
            },
            settings.VERIFY_CHANGE_PASSWORD_TEMPLATE_ID,
        )

    @patch("core.helpers.send_capture_message")
    @patch.object(SendGridAPIClient, "send")
    def test_send_welcome_email_failure(self, mock_send, mock_send_capture_message):
        """
        Test that the send_welcome_email task handles email sending failure.
        """

        mock_send.side_effect = Exception("Email sending failed")
        send_password_reset_email(self.user_data, self.token)
        mock_send_capture_message.assert_called_once()

    @patch.object(SendGridAPIClient, "send")
    def test_send_password_reset_email_success_call_sendgrid(self, mock_send):
        """
        Test that the send_password_reset_email task successfully sends an email.
        """

        send_password_reset_email(self.user_data, self.token)
        mock_send.assert_called_once()
