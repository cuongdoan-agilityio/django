import datetime

from django.contrib import admin
from django.utils import timezone
from django.db import models

from core.models import AbstractBaseModel


class Poll(AbstractBaseModel):
    """Poll model"""

    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Question(AbstractBaseModel):
    """Question model"""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    poll = models.ForeignKey(Poll, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.question_text

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        now = timezone.now()

        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(AbstractBaseModel):
    """Choice model"""

    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.choice_text
