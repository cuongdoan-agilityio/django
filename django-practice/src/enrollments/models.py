from django.db import models

from core.models import AbstractBaseModel


class Enrollment(AbstractBaseModel):
    """
    Enrollment model
    """
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )