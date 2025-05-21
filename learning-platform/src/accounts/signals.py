from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings

from core.helpers import send_email, create_token
from courses.models import Course


User = get_user_model()


@receiver(post_save, sender=User)
def send_verify_email(sender, instance, created, **kwargs):
    """
    Signal to send a verification email to newly created student users.
    """

    if created and instance.is_student:
        dynamic_template_data = {
            "user_name": instance.username,
            "sender_name": settings.SENDER_NAME,
            "subject": "Verification Email",
            "activation_link": f"{settings.API_DOMAIN}/api/v1/auth/confirm-signup-email/?token={create_token(instance.id)}",
        }
        send_email(
            instance.email, dynamic_template_data, settings.VERIFY_SIGNUP_TEMPLATE_ID
        )


@receiver(post_save, sender=User)
def enroll_intro_course(sender, instance, created, **kwargs):
    """
    Signal to automatically enroll newly created student users in intro courses.
    """

    if created and instance.is_student:
        intro_courses = Course.objects.filter(instructor__isnull=True).all()
        instance.enrolled_courses.set(intro_courses)
