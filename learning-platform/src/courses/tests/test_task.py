import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model

from core.constants import Role, Status
from courses.models import Course
from courses.tasks import (
    clean_up_inactive_courses,
    send_monthly_report,
    report_to_instructor,
)
from courses.factories import CourseFactory


User = get_user_model()


@pytest.mark.django_db
class TestCleanUpInactiveCoursesTask:
    """
    Unit tests for the clean_up_inactive_courses Celery task.
    """

    def test_clean_up_inactive_courses_success(self, fake_instructor):
        """
        Test that inactive courses older than 3 months are deleted.
        """

        old_inactive_course = self.fake_course(
            datetime.now() - relativedelta(months=4), instructor=fake_instructor
        )
        clean_up_inactive_courses()
        assert not Course.objects.filter(id=old_inactive_course.id).exists()

    def test_active_courses_not_deleted(self, fake_instructor):
        """
        Test that active courses are not deleted.
        """

        active_course = self.fake_course(
            datetime.now() - relativedelta(months=2),
            Status.ACTIVATE.value,
            instructor=fake_instructor,
        )
        clean_up_inactive_courses()
        assert Course.objects.filter(id=active_course.id).exists()

    def test_recent_inactive_courses_not_deleted(self, fake_instructor):
        """
        Test that inactive courses less than 3 months old are not deleted.
        """

        recent_inactive_course = self.fake_course(
            datetime.now() - relativedelta(months=2), instructor=fake_instructor
        )
        clean_up_inactive_courses()
        assert Course.objects.filter(id=recent_inactive_course.id).exists()

    def test_system_courses_not_deleted(self, fake_instructor):
        """
        Test that system courses are not deleted.
        """

        system_course = self.fake_course(
            datetime.now() - relativedelta(months=4), Status.INACTIVE.value
        )
        clean_up_inactive_courses()
        assert Course.objects.filter(id=system_course.id).exists()

    def fake_course(self, delta_time, status=Status.INACTIVE.value, instructor=None):
        """
        Create a fake course.
        """

        self.patcher = patch("django.utils.timezone.now", return_value=delta_time)
        self.patcher.start()

        course = CourseFactory(
            instructor=instructor,
            status=status,
        )
        self.patcher.stop()

        return course


@pytest.mark.django_db
class TestSendMonthlyReportTask:
    """
    Unit tests for the send_monthly_report Celery task.
    """

    @patch("courses.tasks.report_to_instructor.s")
    @patch("courses.tasks.group")
    def test_send_monthly_report_success(
        self,
        mock_group,
        mock_report_to_instructor,
        fake_instructor,
        math_enrollment,
        math_enrollment_other,
        music_enrollment,
    ):
        """
        Test that the monthly report is sent successfully to instructors.
        """

        mock_group.return_value.apply_async = MagicMock()

        send_monthly_report()
        assert mock_report_to_instructor.called
        assert mock_report_to_instructor.call_count == 1

    def test_no_courses_for_instructor(self):
        """
        Test that the task handles instructors with no courses gracefully.
        """

        Course.objects.all().delete()

        with patch(
            "courses.tasks.send_report_email", return_value=None
        ) as mock_send_report_email:
            send_monthly_report()
            mock_send_report_email.assert_not_called()

    def test_no_instructors_in_system(self):
        """
        Test that the task handles no instructors in the system gracefully.
        """

        User.objects.filter(role=Role.INSTRUCTOR.value).delete()

        with patch(
            "courses.tasks.send_report_email", return_value=None
        ) as mock_send_report_email:
            send_monthly_report()
            mock_send_report_email.assert_not_called()


@pytest.mark.django_db
class TestReportToInstructorTask:
    """
    Unit tests for the report_to_instructor Celery task.
    """

    @patch("courses.tasks.send_report_email")
    def test_report_to_instructor_success(
        self, mock_send_report_email, fake_instructor, math_enrollment, music_enrollment
    ):
        """
        Test that the report_to_instructor task generates the CSV file and sends the email successfully.
        """

        report_to_instructor(fake_instructor.id)
        mock_send_report_email.assert_called_once()

        _, kwargs = mock_send_report_email.call_args
        assert kwargs["instructor"] == fake_instructor
        assert "csv_file" in kwargs

    @patch("courses.tasks.send_report_email")
    def test_report_to_instructor_no_courses(
        self,
        mock_send_report_email,
        fake_instructor,
    ):
        """
        Test that the report_to_instructor task handles no courses gracefully.
        """

        report_to_instructor(fake_instructor.id)
        mock_send_report_email.assert_not_called()

    @patch("courses.tasks.send_report_email")
    def test_report_to_instructor_email_failure(
        self, mock_send_report_email, fake_instructor, math_enrollment, music_enrollment
    ):
        """
        Test that the report_to_instructor task handles email sending failure gracefully.
        """

        mock_send_report_email.side_effect = Exception("Email sending failed")

        with pytest.raises(Exception, match="Email sending failed"):
            report_to_instructor(fake_instructor.id)

        mock_send_report_email.assert_called_once()
