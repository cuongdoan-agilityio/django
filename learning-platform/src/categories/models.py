from django.db import models

from core.models import AbstractBaseModel


class Category(AbstractBaseModel):
    """
    Category model
    """

    name = models.CharField(help_text="Category name", unique=True, max_length=255)

    def __str__(self):
        return self.name
