from django.core.exceptions import ValidationError
import datetime
import re
from django.utils.translation import gettext as _

from core.constants import SPECIAL_CHARACTER_REGEX
from core.error_messages import ErrorMessage


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
        elif char in SPECIAL_CHARACTER_REGEX:
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


class ComplexPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _(ErrorMessage.PASSWORD_UPPERCASE),
                code="password_no_upper",
            )
        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _(ErrorMessage.PASSWORD_LOWERCASE),
                code="password_no_lower",
            )
        if not re.search(r"\d", password):
            raise ValidationError(
                _(ErrorMessage.PASSWORD_NUMBER),
                code="password_no_digit",
            )
        if not re.search(SPECIAL_CHARACTER_REGEX, password):
            raise ValidationError(
                _(ErrorMessage.PASSWORD_SPECIAL_CHAR),
                code="password_no_special",
            )

    def get_help_text(self):
        return _(ErrorMessage.COMPLEX_PASSWORD)


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
