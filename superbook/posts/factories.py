from factory import Faker, SubFactory, Iterator
from factory.django import DjangoModelFactory as ModelFactory

from posts.models.post import Post
from posts.models.superhero import SuperHero


class SuperHeroFactory(ModelFactory):
    """
    Factory for creating SuperHero instances.
    """

    name = Faker("name")
    power = Faker("random_int", min=1, max=100)

    class Meta:
        """
        Meta class
        """

        model = SuperHero


class PostFactory(ModelFactory):
    """
    Faker for creating Post instances.
    """

    hero = SubFactory(SuperHeroFactory)
    content = Faker("paragraph")
    likes = Iterator(range(1, 1000))

    class Meta:
        """
        Meta class
        """

        model = Post
