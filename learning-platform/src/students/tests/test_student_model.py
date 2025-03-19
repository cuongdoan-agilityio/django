import random
from faker import Faker
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from accounts.factories import UserFactory
from core.constants import ScholarshipChoices, Gender
from students.models import Student
from students.factories import StudentFactory


User = get_user_model()
fake = Faker()


class StudentModelTest(TestCase):
    """
    Test case for the Student model.
    """

    def setUp(self):
        """
        Set up the test case with a sample user and student.
        """
        self.username = fake.user_name()
        self.email = fake.email()
        self.scholarship = random.choice(
            [choice.value for choice in ScholarshipChoices]
        )
        self.gender = random.choice([gender.value for gender in Gender])
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
