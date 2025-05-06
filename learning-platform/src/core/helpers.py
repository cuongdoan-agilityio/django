from django.core.signing import TimestampSigner
from rest_framework.response import Response
from sentry_sdk import capture_message
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def create_token(user):
    """
    Create a signing token for the user.
    """

    signer = TimestampSigner()
    value = str(user.id)
    signed_value = signer.sign(value)
    token = urlsafe_base64_encode(force_bytes(signed_value))
    return token


def send_capture_message(data: Response | str) -> str:
    """
    Send a message to Sentry.

    Args:
        data (Response | str): The data to send.

    Returns:
        str: The message sent.
    """

    if isinstance(data, str):
        capture_message(data)

        return data

    try:
        message = str(data.json())
    except Exception:
        message = str(data.text)

    capture_message(message)

    return message
