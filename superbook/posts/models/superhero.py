from django.db import models
from .mixin import TimeStampedMixin


class SuperHero(TimeStampedMixin):
    """
    SuperHero model
    """

    name = models.CharField(max_length=100)
    power = models.CharField(max_length=100)

    def __str__(self):
        return self.name
