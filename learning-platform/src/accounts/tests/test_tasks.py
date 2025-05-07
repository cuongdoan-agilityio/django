from unittest.mock import patch
from accounts.tasks import send_welcome_email
from django.conf import settings
from core.tests.base import BaseTestCase
from sendgrid import SendGridAPIClient


class SendWelcomeEmailTaskTest(BaseTestCase):
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
