from django.dispatch import receiver
from core.helpers import send_email
from django.conf import settings
from courses.models import Course
from django.db.models.signals import m2m_changed


@receiver(m2m_changed, sender=Course.students.through)
def send_email_to_instructor(sender, instance, action, pk_set, **kwargs):
    """
    Send an email to the instructor when course enrollment is created and course has reached its
    enrollment limit

    Args:
        sender (Enrollment): The model class that sent the signal.
        instance (Enrollment): The instance of the model class that sent the signal.
        created (bool): A boolean indicating whether the enrollment instance was created.
        **kwargs: Additional keyword arguments passed to the signal handler.
    """

    if action == "post_add" and isinstance(instance, Course):
        if instance.is_full:
            template_data = {
                "user_name": instance.instructor.username,
                "course_title": instance.title,
                "sender_name": settings.SENDER_NAME,
                "subject": "Course Enrollment Limit Reached",
            }
            send_email(
                email=instance.instructor.email,
                template_data=template_data,
                template_id=settings.INSTRUCTOR_EMAIL_TEMPLATE_ID,
            )
