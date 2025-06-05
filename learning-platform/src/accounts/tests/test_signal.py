import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from unittest.mock import patch

from accounts.factories import UserFactory
from accounts.signals import send_verify_email, enroll_intro_course
from core.constants import Status, Role
from courses.models import Course
from courses.factories import CourseFactory
from core.constants import URL
from .base import BaseAccountModuleTestCase


User = get_user_model()


class TestUserSignals(BaseAccountModuleTestCase):
    """
    Unit tests for the send_verify_email and enroll_intro_course signals.
    """

    @pytest.fixture(autouse=True)
    def send_verify_email_signal():
        """
        Fixture to connect the `send_verify_email` signal for the User model.
        Disconnects the signal after the test to avoid side effects.
        """

        post_save.connect(receiver=send_verify_email, sender=User)
        yield
        post_save.disconnect(receiver=send_verify_email, sender=User)

    @pytest.fixture(autouse=True)
    def enroll_intro_course_signal():
        """
        Fixture to connect the `enroll_intro_course` signal for the User model.
        Disconnects the signal after the test to avoid side effects.
        """

        post_save.connect(receiver=enroll_intro_course, sender=User)
        yield
        post_save.disconnect(receiver=enroll_intro_course, sender=User)

    @patch("accounts.signals.send_email")
    @patch("accounts.signals.create_token")
    def test_send_verify_email_success(self, mock_create_token, mock_send_email):
        """
        Test that send_verify_email signal sends a verification email successfully.
        """

        mock_create_token.return_value = "mocked_token"
        mock_send_email.return_value = None

        user = UserFactory(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

        mock_create_token.assert_called_once_with(user.id)

        mock_send_email.assert_called_once_with(
            user.email,
            {
                "user_name": user.username,
                "sender_name": settings.SENDER_NAME,
                "subject": "Verification Email",
                "activation_link": f"{settings.APP_DOMAIN}/{URL['VERIFY_SIGNUP']}/?token=mocked_token",
            },
            settings.VERIFY_SIGNUP_TEMPLATE_ID,
        )

    @patch("accounts.signals.send_email")
    @patch("accounts.signals.create_token")
    def test_send_verify_email_failure(self, mock_create_token, mock_send_email):
        """
        Test that send_verify_email signal handles email sending failure.
        """

        mock_create_token.return_value = "mocked_token"
        mock_send_email.side_effect = Exception("Email sending failed")

        with pytest.raises(Exception, match="Email sending failed"):
            UserFactory(
                username=self.user_data["username"],
                email=self.user_data["email"],
                password=self.user_data["password"],
            )

        mock_create_token.assert_called_once()
        mock_send_email.assert_called_once()

    @patch("accounts.signals.send_email")
    def test_enroll_intro_course_success(self, mock_send_email):
        """
        Test that enroll_intro_course signal enrolls a student in intro courses.
        """

        mock_send_email.return_value = None
        intro_course = CourseFactory(instructor=None, status=Status.ACTIVATE.value)
        other_intro_course = CourseFactory(
            instructor=None, status=Status.ACTIVATE.value
        )

        user = UserFactory()

        assert intro_course.students.filter(id=user.id).exists()
        assert other_intro_course.students.filter(id=user.id).exists()

    @patch("accounts.signals.send_email")
    def test_enroll_intro_course_no_intro_courses(self, mock_send_email):
        """
        Test that enroll_intro_course signal does nothing if no intro courses exist.
        """

        mock_send_email.return_value = None

        Course.objects.all().delete()

        user = UserFactory()

        assert not user.enrolled_courses.exists()

    @patch("accounts.signals.send_email")
    def test_enroll_intro_course_non_student(self, mock_send_email):
        """
        Test that enroll_intro_course signal does nothing for non-students.
        """

        mock_send_email.return_value = None
        CourseFactory(instructor=None, status=Status.ACTIVATE.value)

        user = UserFactory(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            role=Role.INSTRUCTOR.value,
        )

        assert not user.enrolled_courses.exists()
