import pytest
from faker import Faker
from django.contrib.auth import get_user_model

from accounts.factories import SpecializationFactory


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
def user_data(random_gender):
    """
    Fixture to provide sample user data.
    Includes fields like username, email, and password.
    """

    username = fake.user_name()
    email = fake.email()
    password = "Password@123"
    first_name = fake.first_name()
    last_name = fake.last_name()
    phone_number = "0953625482"
    date_of_birth = fake.date_between(start_date="-60y", end_date="-18y")
    gender = random_gender
    return {
        "username": username,
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "date_of_birth": date_of_birth,
        "gender": gender,
    }


@pytest.fixture
def reset_email_data(user_data):
    """
    Fixture for password reset email data, including a token.
    """

    token = "mocked_token"
    return {**user_data, "token": token}


@pytest.fixture
def specialization(specialization_factory):
    return specialization_factory()
