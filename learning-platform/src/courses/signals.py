from django.db.models.signals import post_save
from django.dispatch import receiver
from core.helpers import send_email
from django.conf import settings

from courses.models import Enrollment


@receiver(post_save, sender=Enrollment)
def send_email_to_instructor(sender, instance, created, **kwargs):
    """
    Send an email to the instructor when course enrollment is created and course has reached its
    enrollment limit

    Args:
        sender (Enrollment): The model class that sent the signal.
        instance (Enrollment): The instance of the model class that sent the signal.
        created (bool): A boolean indicating whether the enrollment instance was created.
        **kwargs: Additional keyword arguments passed to the signal handler.
    """
    if created:
        course = instance.course
        if course.is_full:
            template_data = {
                "user_name": course.instructor.username,
                "course_title": course.title,
                "sender_name": settings.SENDER_NAME,
                "subject": "Course Enrollment Limit Reached",
            }
            send_email(
                email=course.instructor.email,
                template_data=template_data,
                template_id=settings.INSTRUCTOR_EMAIL_TEMPLATE_ID,
            )
