import pytest
from faker import Faker
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from accounts.factories import SpecializationFactory
from accounts.signals import send_verify_email, enroll_intro_course


fake = Faker()
User = get_user_model()


@pytest.fixture
def specialization_data():
    """
    Fixture for creating specialization data.
    """

    name = fake.sentence(nb_words=5)
    description = fake.paragraph(nb_sentences=2)
    return {"name": name, "description": description}


@pytest.fixture
def fake_specialization(specialization_data):
    """
    Fixture for creating a specialization instance.
    """

    return SpecializationFactory(
        **specialization_data
    )


@pytest.fixture
def user_data():
    username = fake.user_name()
    email = fake.email()
    password = "Password@123"
    return {"username": username, "email": email, "password": password}


@pytest.fixture
def send_verify_email_signal():
    post_save.connect(receiver=send_verify_email, sender=User)
    yield
    post_save.disconnect(receiver=send_verify_email, sender=User)


@pytest.fixture
def enroll_intro_course_signal():
    post_save.connect(receiver=enroll_intro_course, sender=User)
    yield
    post_save.disconnect(receiver=enroll_intro_course, sender=User)
