from django.db import models
from django.conf import settings

from core.models import AbstractBaseModel


class Subject(AbstractBaseModel):
    """
    Subject model representing a subject that an instructor can specialize in.

    Attributes:
        name (CharField): The name of the subject.
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Instructor(AbstractBaseModel):
    """
    Instructor model representing an instructor.

    Attributes:
        user (OneToOneField): The user associated with the instructor profile.
        specialization (ManyToManyField): The subjects that the instructor specializes in.
        salary (DecimalField): The salary of the instructor.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
        help_text="The user associated with the instructor profile.",
    )
    specialization = models.ManyToManyField(
        Subject,
        related_name="instructors",
        help_text="The subjects that the instructor specializes in.",
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="The salary of the instructor.",
        default=0.00,
    )

    def __str__(self):
        return self.user.username
