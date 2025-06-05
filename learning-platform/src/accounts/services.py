from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.authtoken.models import Token
from core.exceptions import UserException, TokenException
from core.constants import ScholarshipChoices
from core.helpers import create_token
from accounts.tasks import send_password_reset_email, send_welcome_email


User = get_user_model()


class AuthenticationServices:
    """
    A service class for handling authentication-related operations.
    """

    def handle_create_user(self, validated_data: dict):
        """
        Creates a new user and associated student profile.

        Args:
            validated_data (dict): The validated data for creating the user.

        Returns:
            User: The created user instance.
        """

        try:
            user = User(
                username=validated_data["username"],
                email=validated_data["email"],
                scholarship=ScholarshipChoices.ZERO.value,
                password=validated_data["password"],
                is_active=False,
            )
            user.full_clean()
            user.save()

        except Exception:
            raise UserException(code="USER_CREATION_FAILED")

    def handle_confirm_signup_email(self, token):
        """
        Confirm the email of a user using a token.
        """

        signer = TimestampSigner()

        try:
            signed_value = force_str(urlsafe_base64_decode(token))
            user_id = signer.unsign(signed_value, max_age=24 * 3600)
        except SignatureExpired:
            raise TokenException(code="TOKEN_EXPIRED")
        except (BadSignature, ValueError):
            raise TokenException(code="TOKEN_INVALID")

        try:
            user = User.objects.get(id=user_id)
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])
                user_data = model_to_dict(user, fields=["username", "email"])
                send_welcome_email.delay(user_data)
        except User.DoesNotExist:
            raise UserException(code="USER_NOT_FOUND")

    def handle_reset_password(self, email: str) -> dict:
        """
        Service to handle password reset request by generating a token and sending an email.
        Returns a dict with success status or raises ValidationError on failure.
        """

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise UserException(code="USER_NOT_FOUND")

        token = create_token(user.email)
        send_password_reset_email.delay(
            {"username": user.username, "email": user.email},
            token,
        )

    def handle_confirm_reset_password(self, token: str, password: str) -> dict:
        """
        Service to handle password reset confirmation using a token.
        Returns a dict with success status or raises ValidationError on failure.
        """
        signer = TimestampSigner()

        try:
            signed_value = force_str(urlsafe_base64_decode(token))
            email = signer.unsign(signed_value, max_age=180)
        except SignatureExpired:
            raise TokenException(code="TOKEN_EXPIRED")
        except (BadSignature, ValueError):
            raise TokenException(code="TOKEN_INVALID")

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save(update_fields=["password"])
            Token.objects.filter(user=user).delete()

        except User.DoesNotExist:
            raise UserException(code="USER_NOT_FOUND")


class UserServices:
    """
    A service class for handling user-related operations.
    """

    def update_user_profile(self, user, data):
        """
        Update the profile of a user.
        """

        if "scholarship" in data and not user.is_student:
            data.pop("scholarship")

        if "degree" in data and not user.is_instructor:
            data.pop("degree")

        if "specializations" in data and not user.is_instructor:
            data.pop("specializations")

        update_fields = []

        try:
            for field, value in data.items():
                if field == "specializations":
                    user.specializations.set(value)
                else:
                    setattr(user, field, value)
                    update_fields.append(field)
            user.save(update_fields=update_fields)
        except Exception:
            raise UserException(code="UPDATE_COURSE_FAILED")

        return user
