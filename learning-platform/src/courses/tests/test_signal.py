import pytest
from unittest.mock import patch
from django.conf import settings
from .base import BaseCourseModuleTestCase
from django.db.models.signals import m2m_changed
from courses.models import Course
from courses.signals import send_email_to_instructor


class TestSendEmailToInstructorSignal(BaseCourseModuleTestCase):
    def test_send_email_when_course_is_full(self):
        """
        Test that an email is sent to the instructor when the course reaches its enrollment limit.
        """

        m2m_changed.connect(
            receiver=send_email_to_instructor, sender=Course.students.through
        )
        with patch("courses.signals.send_email", return_value=None) as mock_send_email:
            self.math_course.students.add(self.fake_student, self.fake_other_student)
            mock_send_email.assert_called_once_with(
                email=self.fake_instructor.email,
                template_data={
                    "user_name": self.fake_instructor.username,
                    "course_title": self.math_course.title,
                    "sender_name": settings.SENDER_NAME,
                    "subject": "Course Enrollment Limit Reached",
                },
                template_id=settings.INSTRUCTOR_EMAIL_TEMPLATE_ID,
            )

    def test_no_email_when_course_is_not_full(self):
        """
        Test that no email is sent to the instructor when the course is not full.
        """

        m2m_changed.connect(
            receiver=send_email_to_instructor, sender=Course.students.through
        )

        with patch("courses.signals.send_email", return_value=None) as mock_send_email:
            self.fake_course.students.add(self.fake_student)
            mock_send_email.assert_not_called()

    def test_send_email_failure(self):
        """
        Test that an exception is raised when sending email fails.
        """

        m2m_changed.connect(
            receiver=send_email_to_instructor, sender=Course.students.through
        )

        with patch(
            "courses.signals.send_email", side_effect=Exception("Email sending failed")
        ) as mock_send_email:
            with pytest.raises(Exception, match="Email sending failed"):
                self.math_course.students.add(
                    self.fake_student, self.fake_other_student
                )

            mock_send_email.assert_called_once()
