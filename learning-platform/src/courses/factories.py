from factory import Faker, SubFactory, Iterator, Sequence
from factory.django import DjangoModelFactory as ModelFactory
from instructors.factories import InstructorFactory
from courses.models import Course, Category
from core.constants import Status


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


class CourseFactory(ModelFactory):
    """
    Factory for creating Course instances.
    """

    title = Faker("words")
    description = Faker("words")
    category = SubFactory(CategoryFactory)
    instructor = SubFactory(InstructorFactory)
    status = Iterator(Status.values())

    class Meta:
        model = Course
