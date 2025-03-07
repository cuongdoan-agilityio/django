from django.db import models

from core.models import AbstractBaseModel


class Category(AbstractBaseModel):
    """
    Category model
    """

    name = models.TextField(help_text="Category name", unique=True)

    def __str__(self):
        return self.name
