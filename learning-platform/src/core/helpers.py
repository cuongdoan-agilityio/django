from django.core.signing import TimestampSigner
from django.utils.encoding import force_bytes
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from rest_framework.response import Response
from sentry_sdk import capture_message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
)


def create_token(value: str) -> str:
    """
    Create a signing token for the user.
    """

    signer = TimestampSigner()
    value = str(value)
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


def send_email(email: str, template_data: dict, template_id: str) -> None:
    """
    Send an email using SendGrid.

    Args:
        email (str): recipient email address
        template_data (dict): SendGrid template data
        template_id (str): SendGrid template ID
    """
    try:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=email,
        )
        message.dynamic_template_data = template_data
        message.template_id = template_id
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)

    except Exception as e:
        send_capture_message(e)


def send_report_email(instructor, csv_file):
    """
    Send an email with the CSV file attached.
    """

    try:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=instructor.email,
            subject="Monthly Enrollment Report",
            html_content="Please find attached the monthly enrollment report.",
        )

        attachment = Attachment(
            FileContent(csv_file),
            FileName(f"{instructor.username}_report.csv"),
            FileType("text/csv"),
            Disposition("attachment"),
        )
        message.attachment = attachment
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)

    except Exception as e:
        send_capture_message(e)
