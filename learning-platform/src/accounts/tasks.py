from celery import shared_task
from django.conf import settings

from core.helpers import send_email
from core.constants import URL


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def send_welcome_email(self, user: dict) -> None:
    """
    Send a welcome email to the user after registration.
    """

    try:
        template_data = {
            "user_name": user.get("username"),
            "sender_name": settings.SENDER_NAME,
            "subject": "Welcome to Our Platform",
        }

        send_email(user.get("email"), template_data, settings.WELCOME_TEMPLATE_ID)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def send_password_reset_email(self, user: dict, token: str) -> None:
    """
    Send a password reset email to the user.
    """

    try:
        template_data = {
            "user_name": user.get("username"),
            "sender_name": settings.SENDER_NAME,
            "subject": "Verify Password Change",
            "activation_link": f"{settings.APP_DOMAIN}/{URL['RESET_PASSWORD']}/?token={token}",
        }

        send_email(
            user.get("email"), template_data, settings.VERIFY_RESET_PASSWORD_TEMPLATE_ID
        )
    except Exception as exc:
        raise self.retry(exc=exc)
