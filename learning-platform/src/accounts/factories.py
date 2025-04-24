from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

from factory.django import DjangoModelFactory as ModelFactory
from factory import Faker, Sequence

from accounts.models import Specialization


User = get_user_model()


class UserFactory(ModelFactory):
    """
    Faker for User model.
    """

    password = make_password("Password@user")
    username = Sequence(lambda n: f"user_{n}")
    email = Sequence(lambda n: "user{}@example.com".format(n))

    class Meta:
        """
        Meta class
        """

        model = User
        django_get_or_create = ("username",)

    @classmethod
    def _create(cls, model_class, **kwargs):
        manager = model_class.objects
        return manager.create_user(**kwargs)


class SpecializationFactory(ModelFactory):
    """
    Faker for Specialization model.
    """

    name = Sequence(lambda n: f"Specialization_{n}")
    description = Faker("paragraph")

    class Meta:
        """
        Meta class
        """

        model = Specialization
