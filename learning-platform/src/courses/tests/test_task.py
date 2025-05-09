from datetime import datetime
from dateutil.relativedelta import relativedelta
from unittest.mock import patch

from accounts.factories import UserFactory
from core.tests.base import BaseTestCase
from core.constants import Role, Status
from courses.models import Course
from courses.tasks import clean_up_inactive_courses
from courses.factories import CourseFactory


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
