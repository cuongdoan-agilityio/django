from django.db import models
from django.conf import settings

from core.models import AbstractBaseModel


class Instructor(AbstractBaseModel):
    """
    Instructor model
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor",
    )

    def __str__(self):
        return self.user.username
