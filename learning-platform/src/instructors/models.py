from django.db import models
from django.conf import settings

from core.models import AbstractBaseModel
from core.constants import Degree


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
        max_digits=12,
        decimal_places=3,
        help_text="The salary of the instructor.",
        default=0.00,
    )
    degree = models.CharField(
        null=True,
        choices=Degree.choices(),
        help_text="The degree of the instructor.",
        max_length=9,
    )

    def get_specializations(self):
        return ", ".join([spec.name for spec in self.specialization.all()])

    def __str__(self):
        return self.user.username
