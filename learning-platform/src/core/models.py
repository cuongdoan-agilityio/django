import uuid

from django.db import models
from django_extensions.db.models import TimeStampedModel


class AbstractBaseModel(TimeStampedModel, models.Model):
    """
    Base abstract model that includes "uuid" instead of "id"
    and includes "created", "modified" timestamp fields.
    """

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False
    )

    class Meta:
        abstract = True
