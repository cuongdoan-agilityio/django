from datetime import datetime
from dateutil.relativedelta import relativedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model

from accounts.factories import UserFactory
from core.tests.base import BaseTestCase
from core.constants import Role, Status
from courses.models import Course
from courses.tasks import clean_up_inactive_courses, send_monthly_report
from courses.factories import CourseFactory, EnrollmentFactory


User = get_user_model()


class CleanUpInactiveCoursesTaskTest(BaseTestCase):
    """
    Unit tests for the clean_up_inactive_courses Celery task.
    """

    def setUp(self):
        """
        Set up test data for the task.
        """
        super().setUp()

        self.instructor = UserFactory(
            role=Role.INSTRUCTOR.value,
        )

        delta_time = datetime.now() - relativedelta(months=4)
        self.old_inactive_course = self.fake_course(
            delta_time, instructor=self.instructor
        )
        self.system_course = self.fake_course(delta_time, Status.INACTIVE.value)

        delta_time = datetime.now() - relativedelta(months=2)

        self.recent_inactive_course = self.fake_course(
            delta_time, instructor=self.instructor
        )
        self.active_course = self.fake_course(
            delta_time, Status.ACTIVATE.value, instructor=self.instructor
        )

    def test_clean_up_inactive_courses_success(self):
        """
        Test that inactive courses older than 3 months are deleted.
        """
        clean_up_inactive_courses()

        self.assertFalse(Course.objects.filter(id=self.old_inactive_course.id).exists())

    def test_active_courses_not_deleted(self):
        """
        Test that active courses are not deleted.
        """

        clean_up_inactive_courses()

        self.assertTrue(Course.objects.filter(id=self.active_course.id).exists())

    def test_recent_inactive_courses_not_deleted(self):
        """
        Test that inactive courses less than 3 months old are not deleted.
        """
        clean_up_inactive_courses()

        self.assertTrue(
            Course.objects.filter(id=self.recent_inactive_course.id).exists()
        )

    def test_system_courses_not_deleted(self):
        """
        Test that system courses are not deleted.
        """
        clean_up_inactive_courses()

        self.assertTrue(Course.objects.filter(id=self.system_course.id).exists())

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


class SendMonthlyReportTaskTest(BaseTestCase):
    """
    Unit tests for the send_monthly_report Celery task.
    """

    def setUp(self):
        """
        Set up test data for the task.
        """
        super().setUp()

        self.math_course = CourseFactory(
            title="Math course",
            status=Status.ACTIVATE.value,
            instructor=self.instructor_user,
        )

        self.music_course = CourseFactory(
            title="Music Course",
            status=Status.ACTIVATE.value,
            instructor=self.instructor_user,
        )

        self.mock_other_student = UserFactory(
            role=Role.STUDENT.value,
        )

        EnrollmentFactory(course=self.math_course, student=self.student_user)
        EnrollmentFactory(course=self.math_course, student=self.mock_other_student)
        EnrollmentFactory(course=self.music_course, student=self.student_user)

    @patch("courses.tasks.send_report_email")
    def test_send_monthly_report_success(self, mock_send_report_email):
        """
        Test that the monthly report is sent successfully to instructors.
        """
        mock_send_report_email.return_value = None

        send_monthly_report()

        mock_send_report_email.assert_called_once()
        args, kwargs = mock_send_report_email.call_args
        self.assertEqual(kwargs["instructor"], self.instructor_user)

    @patch("courses.tasks.send_report_email")
    def test_no_courses_for_instructor(self, mock_send_report_email):
        """
        Test that the task handles instructors with no courses gracefully.
        """

        Course.objects.all().delete()
        send_monthly_report()
        mock_send_report_email.assert_not_called()

    @patch("courses.tasks.send_report_email")
    def test_no_instructors_in_system(self, mock_send_report_email):
        """
        Test that the task handles no instructors in the system gracefully.
        """

        User.objects.filter(role=Role.INSTRUCTOR.value).delete()
        send_monthly_report()
        mock_send_report_email.assert_not_called()

    @patch("courses.tasks.send_report_email")
    def test_email_sending_failure(self, mock_send_report_email):
        """
        Test that the task handles email sending failure gracefully.
        """

        mock_send_report_email.side_effect = Exception("Email sending failed")

        try:
            send_monthly_report()
        except Exception as e:
            self.assertEqual(str(e), "Email sending failed")

        mock_send_report_email.assert_called_once()
