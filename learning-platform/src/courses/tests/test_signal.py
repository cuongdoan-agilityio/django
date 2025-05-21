import pytest
from unittest.mock import patch
from django.conf import settings
from courses.factories import EnrollmentFactory


@pytest.mark.django_db
class TestSendEmailToInstructorSignal:
    def test_send_email_when_course_is_full(
        self, fake_instructor, math_course, connect_send_email_to_instructor_signal
    ):
        """
        Test that an email is sent to the instructor when the course reaches its enrollment limit.
        """

        with patch("courses.signals.send_email", return_value=None) as mock_send_email:
            EnrollmentFactory(course=math_course)
            EnrollmentFactory(course=math_course)
            mock_send_email.assert_called_once_with(
                email=fake_instructor.email,
                template_data={
                    "user_name": fake_instructor.username,
                    "course_title": math_course.title,
                    "sender_name": settings.SENDER_NAME,
                    "subject": "Course Enrollment Limit Reached",
                },
                template_id=settings.INSTRUCTOR_EMAIL_TEMPLATE_ID,
            )

    def test_no_email_when_course_is_not_full(
        self, fake_student, fake_course, connect_send_email_to_instructor_signal
    ):
        """
        Test that no email is sent to the instructor when the course is not full.
        """
        with patch("courses.signals.send_email", return_value=None) as mock_send_email:
            fake_course.students.add(fake_student)
            mock_send_email.assert_not_called()

    def test_send_email_failure(
        self, math_course, connect_send_email_to_instructor_signal
    ):
        """
        Test that an exception is raised when sending email fails.
        """

        with patch(
            "courses.signals.send_email", side_effect=Exception("Email sending failed")
        ) as mock_send_email:
            with pytest.raises(Exception, match="Email sending failed"):
                EnrollmentFactory(course=math_course)
                EnrollmentFactory(course=math_course)

            mock_send_email.assert_called_once()
