from django.db import models

from core.models import AbstractBaseModel


class Instructor(AbstractBaseModel):
    """
    Instructor model
    """

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="instructor",
    )

    def __str__(self):
        return self.user.username
