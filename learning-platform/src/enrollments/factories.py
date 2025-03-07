import factory
from factory.django import DjangoModelFactory as ModelFactory
from courses.factories import CourseFactory
from students.factories import StudentFactory
from enrollments.models import Enrollment


class EnrollmentFactory(ModelFactory):
    """
    Factory for creating Enrollment instances.
    """

    class Meta:
        model = Enrollment

    course = factory.SubFactory(CourseFactory)
    student = factory.SubFactory(StudentFactory)
