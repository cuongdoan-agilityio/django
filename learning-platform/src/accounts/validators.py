from django.core.exceptions import ValidationError
import datetime

from core.constants import SPECIAL_CHARACTER
from core.exceptions import ErrorMessage


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


def validate_date_of_birth(dob, is_student=False):
    """
    Validate the date of birth to ensure it is not in the future.
    """

    if not dob:
        return

    today = datetime.date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if (is_student and age < 6) or (not is_student and age < 18) or age > 100:
        raise ValidationError(ErrorMessage.INVALID_DATE_OF_BIRTH)

    return dob
