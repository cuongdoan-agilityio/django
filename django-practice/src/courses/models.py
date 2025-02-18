from django.db import models

from core.models import AbstractBaseModel


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

    def __str__(self):
        return self.title
