from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Enrollment


@receiver(post_save, sender=Enrollment)
def send_email_to_instructor(sender, instance, created, **kwargs):
    if created:
        # Sent email to instructors if a course reaches enrollment limitation.
        pass
