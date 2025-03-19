from factory.django import DjangoModelFactory as ModelFactory
from factory import SubFactory, Iterator, Faker, Sequence, post_generation

from accounts.factories import UserFactory
from instructors.models import Instructor, Subject
from core.constants import Degree


class SubjectFactory(ModelFactory):
    """
    Faker for Subject model.
    """

    name = Sequence(lambda n: f"Subject_{n}")
    description = Faker("words")

    class Meta:
        """
        Meta class
        """

        model = Subject


class InstructorFactory(ModelFactory):
    """
    Faker for Instructor model.
    """

    user = SubFactory(UserFactory)
    degree = Iterator(Degree.values())

    @post_generation
    def subjects(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for subject in extracted:
                self.subjects.add(subject)

    class Meta:
        """
        Meta class
        """

        model = Instructor
