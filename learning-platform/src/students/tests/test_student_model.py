from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from accounts.factories import UserFactory
from core.constants import ScholarshipChoices
from students.models import Student
from students.factories import StudentFactory
from core.tests.base import BaseTestCase


User = get_user_model()


class StudentModelTest(BaseTestCase):
    """
    Test case for the Student model.
    """

    def setUp(self):
        """
        Set up the test case with a sample user and student.
        """

        super().setUp()

        self.username = self.fake.user_name()
        self.email = self.fake.email()
        self.scholarship = self.random_scholarship()
        self.gender = self.random_gender()
        self.user = UserFactory(
            username=self.username,
            email=self.email,
            gender=self.gender,
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

    def test_student_scholarship_choices(self):
        """
        Test that the scholarship field accepts only valid choices.
        """

        valid_scholarships = [choice.value for choice in ScholarshipChoices]
        self.assertIn(self.student.scholarship, valid_scholarships)

    def test_student_gender(self):
        """
        Test that the gender field is correctly set.
        """

        self.assertEqual(self.student.user.gender, self.gender)

    def test_student_email(self):
        """
        Test that the email field is correctly set.
        """

        self.assertEqual(self.student.user.email, self.email)

    def test_student_update_scholarship(self):
        """
        Test updating the scholarship field of a student.
        """

        new_scholarship = ScholarshipChoices.FIFTY.value
        self.student.scholarship = new_scholarship
        self.student.save()
        self.assertEqual(self.student.scholarship, new_scholarship)

    def test_update_student_with_invalid_scholarship(self):
        """
        Test that an invalid scholarship value raises an error.
        """

        with self.assertRaises(ValidationError):
            self.student.scholarship = 150
            self.student.full_clean()

    def test_delete_student(self):
        """
        Test that deleting a student does not delete the associated user.
        """

        self.student.delete()
        self.assertTrue(User.objects.filter(username=self.username).exists())
        self.assertFalse(Student.objects.filter(user=self.user).exists())
