from django.db.models.signals import post_save
from unittest.mock import patch
from django.conf import settings

from accounts.factories import UserFactory
from core.constants import Role
from core.tests.base import BaseTestCase
from courses.models import Enrollment
from courses.factories import CourseFactory, EnrollmentFactory
from courses.signals import send_email_to_instructor


class SendEmailToInstructorSignalTest(BaseTestCase):
    """
    Unit tests for the send_email_to_instructor signal handler.
    """

    def setUp(self):
        """
        Set up test data for the signal.
        """
        super().setUp()

        self.instructor = UserFactory(role=Role.INSTRUCTOR.value)
        self.student = UserFactory(role=Role.STUDENT.value)
        self.course = CourseFactory(
            instructor=self.instructor,
            enrollment_limit=2,
        )

        post_save.connect(receiver=send_email_to_instructor, sender=Enrollment)

    @patch("courses.signals.send_email")
    def test_send_email_when_course_is_full(self, mock_send_email):
        """
        Test that an email is sent to the instructor when the course reaches its enrollment limit.
        """

        EnrollmentFactory(course=self.course)
        EnrollmentFactory(course=self.course)

        mock_send_email.assert_called_once_with(
            email=self.instructor.email,
            template_data={
                "user_name": self.instructor.username,
                "course_title": self.course.title,
                "sender_name": settings.SENDER_NAME,
                "subject": "Course Enrollment Limit Reached",
            },
            template_id=settings.INSTRUCTOR_EMAIL_TEMPLATE_ID,
        )

    @patch("courses.signals.send_email")
    def test_no_email_when_course_is_not_full(self, mock_send_email):
        """
        Test that no email is sent to the instructor when the course is not full.
        """

        Enrollment.objects.create(course=self.course, student=self.student)
        mock_send_email.assert_not_called()

    @patch("courses.signals.send_email")
    def test_send_email_failure(self, mock_send_email):
        """
        Test that an exception is raised when sending email fails.
        """
        mock_send_email.side_effect = Exception("Email sending failed")

        try:
            EnrollmentFactory(course=self.course)
            EnrollmentFactory(course=self.course)

        except Exception as e:
            self.assertEqual(e.args[0], "Email sending failed")

        mock_send_email.assert_called_once()
