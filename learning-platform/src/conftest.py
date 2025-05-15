import pytest
import random
from faker import Faker
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from accounts.signals import send_verify_email, enroll_intro_course
from core.constants import Degree, Gender, ScholarshipChoices, Role


User = get_user_model()


@pytest.fixture
def faker():
    """
    Fixture to provide an isolated Faker instance for generating fake data.
    """

    return Faker()


@pytest.fixture(autouse=True)
def disconnect_send_verify_email_signal():
    """
    Fixture to disconnect the signal.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)


@pytest.fixture
def random_gender():
    """
    Fixture for random gender data.
    """

    genders = [gender.value for gender in Gender]
    return random.choice(genders)


@pytest.fixture
def student_role():
    """
    Fixture for student role.
    """

    return Role.STUDENT.value


@pytest.fixture
def instructor_role():
    """
    Fixture for instructor role.
    """

    return Role.INSTRUCTOR.value


@pytest.fixture
def admin_role():
    """
    Fixture for admin role.
    """

    return Role.ADMIN.value


@pytest.fixture
def random_scholarship():
    """
    Fixture for random scholarship.
    """

    scholarships = [choice.value for choice in ScholarshipChoices]
    return random.choice(scholarships)


@pytest.fixture
def random_degree():
    """
    Fixture for random degree.
    """

    degrees = [choice.value for choice in Degree]
    return random.choice(degrees)


@pytest.fixture
def send_verify_email_signal():
    """
    Fixture to connect the `send_verify_email` signal for the User model.
    Disconnects the signal after the test to avoid side effects.
    """

    post_save.connect(receiver=send_verify_email, sender=User)
    yield
    post_save.disconnect(receiver=send_verify_email, sender=User)


@pytest.fixture
def enroll_intro_course_signal():
    """
    Fixture to connect the `enroll_intro_course` signal for the User model.
    Disconnects the signal after the test to avoid side effects.
    """

    post_save.connect(receiver=enroll_intro_course, sender=User)
    yield
    post_save.disconnect(receiver=enroll_intro_course, sender=User)
