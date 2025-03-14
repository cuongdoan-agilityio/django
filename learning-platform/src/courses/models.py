from django.db import models

from core.models import AbstractBaseModel
from core.constants import Status


class Category(AbstractBaseModel):
    """
    Category model
    """

    name = models.CharField(help_text="Category name", unique=True, max_length=255)
    description = models.TextField(
        help_text="Category description", blank=True, null=True
    )

    def __str__(self):
        return self.name


class Course(AbstractBaseModel):
    """
    Course model
    """

    title = models.CharField(help_text="Course title", max_length=255)
    description = models.TextField(help_text="Course description")
    category = models.ForeignKey(
        Category,
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
