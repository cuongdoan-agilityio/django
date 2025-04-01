from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    Profile model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hero_name = models.CharField(max_length=100)
    power = models.CharField(max_length=100)

    def __str__(self):
        return self.hero_name
