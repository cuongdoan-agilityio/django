from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .constants import SPECIAL_CHARACTER
from .exceptions import ErrorMessage


User = get_user_model()


def validate_password(password):
    """
    Validate the password to ensure it meets complexity requirements.
    """

    if not password:
        return

    has_lower = has_upper = has_digit = has_special = False
    for char in password:
        if char.islower():
            has_lower = True
        elif char.isupper():
            has_upper = True
        elif char.isdigit():
            has_digit = True
        elif char in SPECIAL_CHARACTER:
            has_special = True

        if has_lower and has_upper and has_digit and has_special:
            break

    if not has_lower:
        raise ValidationError(ErrorMessage.PASSWORD_LOWERCASE)

    if not has_upper:
        raise ValidationError(ErrorMessage.PASSWORD_UPPERCASE)

    if not has_digit:
        raise ValidationError(ErrorMessage.PASSWORD_NUMBER)

    if not has_special:
        raise ValidationError(ErrorMessage.PASSWORD_SPECIAL_CHAR)

    return password


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


def validate_phone_number(phone_number):
    """
    Validate the phone number to ensure it contains only digits and is of valid length.
    """

    if not phone_number:
        return

    if not phone_number.isdigit():
        raise ValidationError(ErrorMessage.PHONE_NUMBER_ONLY_NUMBER)
    if len(phone_number) < 10 or len(phone_number) > 11:
        raise ValidationError(ErrorMessage.PHONE_NUMBER_INVALID_LENGTH)
    return phone_number
