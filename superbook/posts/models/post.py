from django.db import models
from .superhero import SuperHero
from .mixin import TimeStampedMixin


class ActivePostManager(models.Manager):
    """
    ActivePostManager
    """

    def get_queryset(self):
        return super().get_queryset().filter(content__icontains="active")


class Post(TimeStampedMixin):
    """
    Post model.
    """

    hero = models.ForeignKey(SuperHero, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    likes = models.IntegerField(default=0)
    title = models.CharField(max_length=255, null=True, blank=True)

    objects = models.Manager()
    active_objects = ActivePostManager()

    def __str__(self):
        return f"{self.hero.name}: {self.content}"
