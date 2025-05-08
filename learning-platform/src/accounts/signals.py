from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings

from core.helpers import send_email, create_token
from courses.models import Course, Enrollment


User = get_user_model()


@receiver(post_save, sender=User)
def send_verify_email(sender, instance, created, **kwargs):
    if created:
        dynamic_template_data = {
            "user_name": instance.username,
            "token": create_token(instance.id),
            "sender_name": settings.SENDER_NAME,
            "subject": "Verification Email",
        }
        send_email(
            instance.email, dynamic_template_data, settings.VERIFY_SIGNUP_TEMPLATE_ID
        )


@receiver(post_save, sender=User)
def enroll_intro_course(sender, instance, created, **kwargs):
    if created and instance.is_student:
        intro_courses = Course.objects.filter(instructor__isnull=True)

        for course in intro_courses:
            Enrollment.objects.get_or_create(student=instance, course=course)
