from categories.models import Category
from factory.django import DjangoModelFactory as ModelFactory
from factory import Sequence


class CategoryFactory(ModelFactory):
    """
    Faker for Category model.
    """

    name = Sequence(lambda n: f"Category_{n}")

    class Meta:
        """
        Meta class
        """

        model = Category
        django_get_or_create = ("name",)
