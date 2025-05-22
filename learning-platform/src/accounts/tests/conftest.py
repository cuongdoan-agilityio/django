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
    Fixture to create a specialization instance using the provided specialization data.
    """

    return SpecializationFactory(**specialization_data)


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
    date_of_birth = fake.date_between(start_date="-90y", end_date="-18y")
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
    Fixture to provide password reset email data.
    Includes user data and a mocked token for testing.
    """

    token = "mocked_token"
    return {**user_data, "token": token}


@pytest.fixture
def specialization():
    """
    Fixture to create a specialization instance.
    """

    return SpecializationFactory()


@pytest.fixture
def specializations(db, faker):
    """
    Fixture to create sample specializations.
    """

    return [
        SpecializationFactory(),
        SpecializationFactory(),
    ]


@pytest.fixture
def student_data(user_data, student_role, random_scholarship):
    """
    Fixture to create a specialization instance.
    """

    return {**user_data, "role": student_role, "scholarship": str(random_scholarship)}


@pytest.fixture
def instructor_data(user_data, random_degree, specialization, instructor_role):
    """
    Fixture for instructor-specific data.
    """

    instructor_data = {
        **user_data,
        "username": fake.user_name(),
        "email": fake.email(),
        "role": instructor_role,
        "specializations": [str(specialization.id)],
        "degree": random_degree,
    }
    return instructor_data


@pytest.fixture
def user_retrieve_url(root_url):
    """
    Fixture to provide the retrieve URL for user profiles.
    """

    return f"{root_url}users/me/"


@pytest.fixture
def user_url(root_url):
    """
    Fixture to provide the user url.
    """

    return f"{root_url}users/"


@pytest.fixture
def specialization_url(root_url):
    """
    Fixture to provide the base URL for specializations.
    """

    return f"{root_url}specializations/"
