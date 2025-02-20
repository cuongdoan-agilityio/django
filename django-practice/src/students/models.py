from django.db import models
from django.conf import settings
from core.models import AbstractBaseModel


class Student(AbstractBaseModel):
    """
    Student model
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    def __str__(self):
        return self.user.username
