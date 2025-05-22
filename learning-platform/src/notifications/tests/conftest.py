import pytest
from faker import Faker
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from accounts.signals import send_verify_email
from accounts.factories import UserFactory
from core.constants import Role
from notifications.factories import NotificationFactory


fake = Faker()
User = get_user_model()


@pytest.fixture
def share_data():
    return {
        "password": "Password@123",
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "message": fake.sentence(),
        "is_read": fake.boolean(),
    }


@pytest.fixture
def fake_user(share_data):
    post_save.disconnect(receiver=send_verify_email, sender=User)
    return UserFactory(
        password=share_data["password"],
        username=share_data["username"],
        email=share_data["email"],
        role=Role.STUDENT.value,
    )


@pytest.fixture
def fake_notification(fake_user, share_data):
    return NotificationFactory(
        user=fake_user,
        message=share_data["message"],
        is_read=share_data["is_read"],
    )


@pytest.fixture
def notification_url(root_url):
    """
    Fixture to provide the base URL for notifications list.
    """
    return f"{root_url}notifications/"


@pytest.fixture
def fake_student_notifications(fake_student):
    """
    Fixture to create notifications for the student user.
    """
    return [
        NotificationFactory(user=fake_student, is_read=False),
        NotificationFactory(user=fake_student, is_read=True),
    ]


@pytest.fixture
def fake_instructor_notifications(fake_instructor):
    """
    Fixture to create notifications for the instructor user.
    """

    return [
        NotificationFactory(user=fake_instructor, is_read=False),
        NotificationFactory(user=fake_instructor, is_read=True),
    ]
