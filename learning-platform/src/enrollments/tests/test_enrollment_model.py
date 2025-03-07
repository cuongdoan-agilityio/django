from django.test import TestCase
from enrollments.models import Enrollment
from enrollments.factories import EnrollmentFactory
from courses.factories import CourseFactory
from students.factories import StudentFactory


class EnrollmentModelTest(TestCase):
    """
    Test case for the Enrollment model.
    """

    def setUp(self):
        """
        Set up the test case with a sample enrollment.
        """

        self.course = CourseFactory()
        self.student = StudentFactory()
        self.enrollment = EnrollmentFactory(course=self.course, student=self.student)

    def test_enrollment_creation(self):
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

        self.assertEqual(self.enrollment.student, self.student)
