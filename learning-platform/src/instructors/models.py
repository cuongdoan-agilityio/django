from django.db import models
from django.conf import settings

from core.models import AbstractBaseModel
from core.constants import Degree
from courses.models import Course


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
        subjects (ManyToManyField): The subjects that the instructor specializes in.
        degree (Degree): The instructor degree.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
        help_text="The user associated with the instructor profile.",
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name="instructors",
        help_text="The subjects that the instructor specializes in.",
    )
    degree = models.CharField(
        choices=Degree.choices(),
        default=Degree.NO.value,
        help_text="The degree of the instructor.",
        max_length=9,
    )

    def get_subjects(self):
        return ", ".join([spec.name for spec in self.subjects.all()])

    def get_courses(self):
        return ", ".join(
            [spec.title for spec in Course.objects.filter(instructor=self)]
        )

    def __str__(self):
        return self.user.username
