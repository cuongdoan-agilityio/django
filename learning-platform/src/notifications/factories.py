from factory import Faker, SubFactory
from factory.django import DjangoModelFactory as ModelFactory

from accounts.factories import UserFactory
from notifications.models import Notification


class NotificationFactory(ModelFactory):
    """
    Factory for creating Notification instances.
    """

    message = Faker("sentence")
    user = SubFactory(UserFactory)
    is_read = Faker("boolean")

    class Meta:
        """
        Meta class for NotificationFactory.
        """

        model = Notification
        django_get_or_create = ("user", "message")
