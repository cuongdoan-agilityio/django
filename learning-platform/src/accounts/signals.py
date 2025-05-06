from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from core.helpers import create_token, send_capture_message
from courses.models import Course, Enrollment


User = get_user_model()


def send_email(user):
    try:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=user.email,
        )
        message.dynamic_template_data = {
            "user_email": user.email,
            "token": create_token(user),
            "sender_name": settings.SENDER_NAME,
            "subject": "Verification Email",
        }
        message.template_id = settings.VERIFY_SIGNUP_TEMPLATE_ID
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        return send_capture_message(e)


@receiver(post_save, sender=User)
def send_verify_email(sender, instance, created, **kwargs):
    if created:
        send_email(instance)


@receiver(post_save, sender=User)
def enroll_intro_course(sender, instance, created, **kwargs):
    if created and instance.is_student:
        intro_courses = Course.objects.filter(instructor__isnull=True)

        for course in intro_courses:
            Enrollment.objects.get_or_create(student=instance, course=course)
