from django.core.exceptions import ValidationError
from courses.models import Enrollment
from courses.factories import CourseFactory, EnrollmentFactory
from core.constants import Status
from core.tests.base import BaseTestCase


class EnrollmentModelTest(BaseTestCase):
    """
    Test case for the Enrollment model.
    """

    def setUp(self):
        """
        Set up the test case with a sample enrollment.
        """
        super().setUp()

        self.course = CourseFactory(status=Status.ACTIVATE.value)
        self.enrollment = EnrollmentFactory(
            course=self.course, student=self.student_user
        )

    def test_enrollment_success(self):
        """
        Test that an enrollment can be created successfully.
        """

        self.assertIsInstance(self.enrollment, Enrollment)

    def test_enrollment_course_relationship(self):
        """
        Test the relationship between Enrollment and Course.
        """

        self.assertEqual(self.enrollment.course, self.course)

    def test_enrollment_student_relationship(self):
        """
        Test the relationship between Enrollment and Student.
        """

        self.assertEqual(self.enrollment.student, self.student_user)

    def test_enrollment_without_course(self):
        """
        Test that an enrollment cannot be created with an invalid course.
        """

        with self.assertRaises(ValidationError):
            invalid_enrollment = EnrollmentFactory.build(course=None)
            invalid_enrollment.full_clean()

    def test_enrollment_without_student(self):
        """
        Test that an enrollment cannot be created with an invalid student.
        """

        with self.assertRaises(ValidationError):
            invalid_enrollment = EnrollmentFactory.build(course=self.course)
            invalid_enrollment.full_clean()
