from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import AbstractBaseModel
from core.constants import ScholarshipChoices


class Student(AbstractBaseModel):
    """
    Student model representing a student.

    Attributes:
        user (OneToOneField): The user associated with the student profile.
        scholarship (CharField): The scholarship amount for the student.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        help_text="The user associated with the student profile.",
    )
    scholarship = models.IntegerField(
        choices=ScholarshipChoices.choices(),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="The scholarship amount for the student.",
        db_index=True,
    )

    def __str__(self):
        """
        Returns the string representation of the student.
        """
        return self.user.username
