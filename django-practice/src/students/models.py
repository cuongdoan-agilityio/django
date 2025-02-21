from django.db import models
from django.conf import settings
from core.models import AbstractBaseModel


class Student(AbstractBaseModel):
    """
    Student model representing a student.

    Attributes:
        SCHOLARSHIP_CHOICES (list): The scholarship choices available for the student.
        user (OneToOneField): The user associated with the student profile.
        scholarship (CharField): The scholarship amount for the student.
    """

    SCHOLARSHIP_CHOICES = [
        (0, "0%"),
        (25, "25%"),
        (50, "50%"),
        (75, "75%"),
        (100, "100%"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    scholarship = models.CharField(
        max_length=3,
        choices=SCHOLARSHIP_CHOICES,
        default=0,
        help_text="The scholarship amount for the student.",
    )

    def __str__(self):
        """
        Returns the string representation of the student.
        """
        return self.user.username
