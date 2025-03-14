from django.db import models

from core.models import AbstractBaseModel


class Enrollment(AbstractBaseModel):
    """
    Enrollment model
    """

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.student.user.first_name} enrolled in {self.course.title}"
