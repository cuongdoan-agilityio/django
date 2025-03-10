from django.test import TestCase
from django.contrib.auth import get_user_model
from students.models import Student
from core.constants import ScholarshipChoices

from students.factories import StudentFactory
from accounts.factories import UserFactory

User = get_user_model()


class StudentModelTest(TestCase):
    """
    Test case for the Student model.
    """

    def setUp(self):
        """
        Set up the test case with a sample user and student.
        """
        self.username = "testuser"
        self.email = "testuser@example.com"
        self.password = "Password@1234"
        self.scholarship = ScholarshipChoices.FULL.value
        self.user = UserFactory(
            username=self.username, email=self.email, password=self.password
        )
        self.student = StudentFactory(user=self.user, scholarship=self.scholarship)

    def test_student_creation(self):
        """
        Test that a student can be created successfully.
        """

        self.assertEqual(self.student.user.username, self.username)
        self.assertEqual(self.student.scholarship, self.scholarship)
        self.assertIsInstance(self.student, Student)

    def test_student_str(self):
        """
        Test the string representation of the student.
        """

        self.assertEqual(str(self.student), self.username)
