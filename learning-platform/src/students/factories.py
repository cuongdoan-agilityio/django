from django.contrib.auth import get_user_model

from factory.django import DjangoModelFactory as ModelFactory
from factory import SubFactory, Iterator

from core.constants import ScholarshipChoices
from accounts.factories import UserFactory
from students.models import Student


User = get_user_model()


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
