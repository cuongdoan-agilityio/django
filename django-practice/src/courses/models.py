from django.db import models
from enum import Enum

from core.models import AbstractBaseModel


class Status(Enum):
    """
    Status class representing different status for courses
    """

    ACTIVATE = "activate"
    INACTIVE = "inactive"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Course(AbstractBaseModel):
    """
    Course model
    """

    title = models.TextField(help_text="Course title")
    description = models.TextField(help_text="Course description")
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.CASCADE,
        help_text="Course category.",
        related_name="courses",
    )
    instructor = models.ForeignKey(
        "instructors.Instructor",
        on_delete=models.CASCADE,
        help_text="Course Instructor.",
        related_name="courses",
    )
    status = models.CharField(
        choices=Status.choices(),
        help_text="Status of the course.",
        max_length=8,
        default=Status.ACTIVATE.value,
    )

    def __str__(self):
        return self.title
