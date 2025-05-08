from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth import get_user_model
from unittest.mock import patch

from accounts.signals import send_verify_email, enroll_intro_course
from accounts.factories import UserFactory
from core.tests.base import BaseTestCase
from core.constants import Status, Role
from courses.models import Course, Enrollment
from courses.factories import CourseFactory


User = get_user_model()


class UserSignalsTest(BaseTestCase):
    """
    Unit tests for the send_verify_email and enroll_intro_course signals.
    """

    def setUp(self):
        """
        Set up test data for the signals.
        """
        super().setUp()

        self.username = self.fake.user_name()
        self.email = self.fake.email()
        self.password = "Password@123"

        post_save.connect(receiver=send_verify_email, sender=User)
        post_save.connect(receiver=enroll_intro_course, sender=User)

    @patch("accounts.signals.send_email")
    @patch("accounts.signals.create_token")
    def test_send_verify_email_success(self, mock_create_token, mock_send_email):
        """
        Test that send_verify_email signal sends a verification email successfully.
        """
        mock_create_token.return_value = "mocked_token"
        mock_send_email.return_value = None

        username = self.fake.user_name()
        email = self.fake.email()

        user = UserFactory(
            username=username,
            email=email,
            password=self.password,
        )

        mock_create_token.assert_called_once_with(user.id)

        mock_send_email.assert_called_once_with(
            user.email,
            {
                "user_name": user.username,
                "token": "mocked_token",
                "sender_name": settings.SENDER_NAME,
                "subject": "Verification Email",
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

        try:
            UserFactory(
                username=self.username,
                email=self.fake.email(),
                password=self.password,
            )

        except Exception as e:
            self.assertEqual(e.args[0], "Email sending failed")

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

        self.assertTrue(
            Enrollment.objects.filter(student=user, course=intro_course).exists()
        )
        self.assertTrue(
            Enrollment.objects.filter(student=user, course=other_intro_course).exists()
        )

    @patch("accounts.signals.send_email")
    def test_enroll_intro_course_no_intro_courses(self, mock_send_email):
        """
        Test that enroll_intro_course signal does nothing if no intro courses exist.
        """

        mock_send_email.return_value = None

        Course.objects.all().delete()

        user = UserFactory()

        self.assertFalse(Enrollment.objects.filter(student=user).exists())

    @patch("accounts.signals.send_email")
    def test_enroll_intro_course_non_student(self, mock_send_email):
        """
        Test that enroll_intro_course signal does nothing for non-students.
        """

        mock_send_email.return_value = None
        CourseFactory(instructor=None, status=Status.ACTIVATE.value)

        user = UserFactory(
            username=self.fake.user_name(),
            email=self.fake.email(),
            password=self.password,
            role=Role.INSTRUCTOR.value,
        )

        self.assertFalse(Enrollment.objects.filter(student=user).exists())
