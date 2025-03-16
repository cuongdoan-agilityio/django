from factory import Faker, SubFactory, Iterator, Sequence
from factory.django import DjangoModelFactory as ModelFactory
from instructors.factories import InstructorFactory
from courses.models import Course, Category, Enrollment
from core.constants import Status
from students.factories import StudentFactory


class CategoryFactory(ModelFactory):
    """
    Faker for Category model.
    """

    name = Sequence(lambda n: f"Category_{n}")
    description = Faker("words")

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


class EnrollmentFactory(ModelFactory):
    """
    Factory for creating Enrollment instances.
    """

    class Meta:
        model = Enrollment

    course = SubFactory(CourseFactory)
    student = SubFactory(StudentFactory)
