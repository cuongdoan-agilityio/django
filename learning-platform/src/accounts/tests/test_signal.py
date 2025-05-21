import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from unittest.mock import patch

from accounts.factories import UserFactory
from core.constants import Status, Role
from courses.models import Course
from courses.factories import CourseFactory


User = get_user_model()


@pytest.mark.django_db
class TestUserSignals:
    """
    Unit tests for the send_verify_email and enroll_intro_course signals.
    """

    @patch("accounts.signals.send_email")
    @patch("accounts.signals.create_token")
    def test_send_verify_email_success(
        self, mock_create_token, mock_send_email, user_data, send_verify_email_signal
    ):
        """
        Test that send_verify_email signal sends a verification email successfully.
        """

        mock_create_token.return_value = "mocked_token"
        mock_send_email.return_value = None

        user = UserFactory(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
        )

        mock_create_token.assert_called_once_with(user.id)

        mock_send_email.assert_called_once_with(
            user.email,
            {
                "user_name": user.username,
                "sender_name": settings.SENDER_NAME,
                "subject": "Verification Email",
                "activation_link": f"{settings.API_DOMAIN}/api/v1/auth/confirm-signup-email/?token=mocked_token",
            },
            settings.VERIFY_SIGNUP_TEMPLATE_ID,
        )

    @patch("accounts.signals.send_email")
    @patch("accounts.signals.create_token")
    def test_send_verify_email_failure(
        self, mock_create_token, mock_send_email, user_data, send_verify_email_signal
    ):
        """
        Test that send_verify_email signal handles email sending failure.
        """

        mock_create_token.return_value = "mocked_token"
        mock_send_email.side_effect = Exception("Email sending failed")

        with pytest.raises(Exception, match="Email sending failed"):
            UserFactory(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
            )

        mock_create_token.assert_called_once()
        mock_send_email.assert_called_once()

    @patch("accounts.signals.send_email")
    def test_enroll_intro_course_success(
        self, mock_send_email, enroll_intro_course_signal
    ):
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
    def test_enroll_intro_course_no_intro_courses(
        self, mock_send_email, enroll_intro_course_signal
    ):
        """
        Test that enroll_intro_course signal does nothing if no intro courses exist.
        """

        mock_send_email.return_value = None

        Course.objects.all().delete()

        user = UserFactory()

        assert not user.enrolled_courses.exists()

    @patch("accounts.signals.send_email")
    def test_enroll_intro_course_non_student(
        self, mock_send_email, user_data, enroll_intro_course_signal
    ):
        """
        Test that enroll_intro_course signal does nothing for non-students.
        """

        mock_send_email.return_value = None
        CourseFactory(instructor=None, status=Status.ACTIVATE.value)

        user = UserFactory(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
            role=Role.INSTRUCTOR.value,
        )

        assert not user.enrolled_courses.exists()
