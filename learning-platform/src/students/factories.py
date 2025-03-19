from factory.django import DjangoModelFactory as ModelFactory
from factory import SubFactory, Iterator

from core.constants import ScholarshipChoices
from accounts.factories import UserFactory
from students.models import Student


class StudentFactory(ModelFactory):
    """
    Faker for Student model.
    """

    user = SubFactory(UserFactory)
    scholarship = Iterator(ScholarshipChoices.values())

    class Meta:
        """
        Meta class
        """

        model = Student
