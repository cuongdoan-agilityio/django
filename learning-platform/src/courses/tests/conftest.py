import pytest
from courses.factories import CourseFactory, CategoryFactory
from faker import Faker
from django.db.models.signals import post_save
from accounts.signals import send_verify_email
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.fixture
def faker():
    """
    Fixture to provide an isolated Faker instance.
    """

    return Faker()


@pytest.fixture
def share_data(faker):
    return {
        "password": "Password@123",
        "username": faker.user_name(),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "email": faker.email(),
        "message": faker.sentence(),
        "is_read": faker.boolean(),
    }


@pytest.fixture
def course_data(faker):
    """Fixture to provide sample course data."""
    title = faker.sentence(nb_words=6)
    description = faker.paragraph(nb_sentences=3)
    return {"title": title, "description": description}


@pytest.fixture
def fake_course(course_data, db):
    """
    Fixture to create a sample Course instance.
    """

    post_save.disconnect(receiver=send_verify_email, sender=User)
    return CourseFactory(
        title=course_data["title"], description=course_data["description"]
    )


@pytest.fixture
def category_data(faker):
    """
    Fixture to provide sample category data.
    """

    return {
        "name": faker.sentence(nb_words=6),
        "description": faker.paragraph(nb_sentences=2),
    }


@pytest.fixture
def fake_category(category_data):
    """
    Fixture to create a Category instance.
    """
    return CategoryFactory(**category_data)
