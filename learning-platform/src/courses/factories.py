from factory import Faker, SubFactory, Iterator
from factory.django import DjangoModelFactory as ModelFactory
from categories.factories import CategoryFactory
from instructors.factories import InstructorFactory
from courses.models import Course
from core.constants import Status


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
