import pytest
import random
from faker import Faker
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.signals import send_verify_email, enroll_intro_course
from core.constants import Degree, Gender, ScholarshipChoices, Role
from accounts.factories import UserFactory


User = get_user_model()


@pytest.fixture(scope="session")
def faker():
    """
    Fixture to provide an isolated Faker instance for generating fake data.
    """

    return Faker()


@pytest.fixture(scope="session")
def root_url():
    return "/api/v1/"


@pytest.fixture(autouse=True)
def disconnect_send_verify_email_signal():
    """
    Fixture to disconnect the signal.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
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


@pytest.fixture
def enroll_intro_course_signal():
    """
    Fixture to connect the `enroll_intro_course` signal for the User model.
    Disconnects the signal after the test to avoid side effects.
    """

    post_save.connect(receiver=enroll_intro_course, sender=User)


@pytest.fixture(scope="session")
def api_client():
    """
    Fixture to provide an API client for making requests.
    """

    return APIClient()


@pytest.fixture()
def share_user_data(faker, random_degree):
    """
    Fixture to provide an user data include student and instructor.
    """

    password = "Password@123"

    return {
        "student": {
            "password": password,
            "username": faker.user_name(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(),
        },
        "other_student": {
            "password": password,
            "username": faker.user_name(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(),
        },
        "instructor": {
            "password": password,
            "username": faker.user_name(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "email": faker.email(),
            "degree": random_degree,
        },
    }


@pytest.fixture()
def fake_student(faker, share_user_data):
    """
    Fixture to create a sample student user instance.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)
    data = share_user_data.get("student")

    return UserFactory(
        password=data.get("password"),
        username=data.get("username"),
        email=data.get("email"),
        role=Role.STUDENT.value,
    )


@pytest.fixture()
def fake_student_token(fake_student):
    """
    Fixture to create a authentication token for student user.
    """

    return Token.objects.create(user=fake_student)


@pytest.fixture()
def fake_instructor(faker, share_user_data):
    """
    Fixture to create instructor user.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)
    data = share_user_data.get("instructor")

    return UserFactory(
        username=data.get("username"),
        password=data.get("password"),
        email=data.get("email"),
        role=Role.INSTRUCTOR.value,
    )


@pytest.fixture
def fake_other_student(faker, share_user_data):
    """
    Fixture to create a sample student user instance.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)
    data = share_user_data.get("other_student")

    return UserFactory(
        password=data.get("password"),
        username=data.get("username"),
        email=data.get("email"),
        role=Role.STUDENT.value,
    )


@pytest.fixture()
def fake_admin(faker):
    """
    Fixture to create instructor user.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)

    return UserFactory(
        username=faker.user_name(),
        password="Password@123",
        email=faker.email(),
        role=Role.ADMIN.value,
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def fake_instructor_token(fake_instructor):
    """
    Fixture to create and return a token for the instructor user.
    """

    return Token.objects.create(user=fake_instructor)


@pytest.fixture
def fake_admin_token(fake_admin):
    """
    Fixture to create and return a token for the instructor user.
    """

    return Token.objects.create(user=fake_admin)
