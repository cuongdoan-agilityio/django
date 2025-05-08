from celery import shared_task
from django.conf import settings

from core.helpers import send_email


@shared_task
def send_welcome_email(user: dict) -> None:
    """
    Send a welcome email to the user after registration.
    """
    template_data = {
        "user_name": user.get("username"),
        "sender_name": settings.SENDER_NAME,
        "subject": "Welcome to Our Platform",
    }

    send_email(user.get("email"), template_data, settings.WELCOME_TEMPLATE_ID)


@shared_task
def send_password_reset_email(user: dict, token: str) -> None:
    """
    Send a password reset email to the user.
    """

    template_data = {
        "user_name": user.get("username"),
        "token": token,
        "sender_name": settings.SENDER_NAME,
        "subject": "Verify Password Change",
    }

    send_email(
        user.get("email"), template_data, settings.VERIFY_CHANGE_PASSWORD_TEMPLATE_ID
    )
