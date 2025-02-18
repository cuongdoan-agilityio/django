from django.db import models

from core.models import AbstractBaseModel


class Category(AbstractBaseModel):
    """
    Category model
    """

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="student",
    )

    def __str__(self):
        return self.user.username
