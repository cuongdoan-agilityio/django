from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def send_verify_email(sender, instance, created, **kwargs):
    if created:
        # Sent email welcome new user to our system.
        pass


@receiver(post_save, sender=User)
def enroll_intro_course(sender, instance, created, **kwargs):
    if created:
        # Enroll user to intro course.
        pass
