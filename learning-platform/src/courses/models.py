from django.db import models

from core.models import AbstractBaseModel
from core.constants import Status


class Course(AbstractBaseModel):
    """
    Course model
    """

    title = models.CharField(help_text="Course title", max_length=255)
    description = models.CharField(help_text="Course description", max_length=300)
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.CASCADE,
        help_text="Course category.",
        related_name="courses",
    )
    instructor = models.ForeignKey(
        "instructors.Instructor",
        help_text="Course Instructor.",
        related_name="courses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=Status.choices(),
        help_text="Status of the course.",
        max_length=8,
        default=Status.ACTIVATE.value,
    )

    def __str__(self):
        return self.title
