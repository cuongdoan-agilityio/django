from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .error_messages import ErrorMessage


User = get_user_model()


def validate_email(email):
    """
    Validate that the email is unique.
    """

    if User.objects.filter(email=email).exists():
        raise ValidationError(ErrorMessage.EMAIL_EXISTS)
    return email


def validate_username(username):
    """
    Validate that the username is unique.
    """

    if User.objects.filter(username=username).exists():
        raise ValidationError(ErrorMessage.USERNAME_EXISTS)
    return username
