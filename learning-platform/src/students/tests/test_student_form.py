import random
from faker import Faker
from django.test import TestCase

from students.forms import StudentBaseForm, StudentEditForm
from students.models import Student
from students.factories import StudentFactory
from accounts.factories import UserFactory
from core.constants import Gender, ScholarshipChoices
from core.exceptions import ErrorMessage
from utils.helpers import random_birthday, random_phone_number


fake = Faker()


class StudentBaseFormTest(TestCase):
    """
    Test case for the StudentBaseForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        self.gender = random.choice([gender.value for gender in Gender])
        self.scholarship = random.choice(
            [scholarship.value for scholarship in ScholarshipChoices]
        )
        self.create_data = {
            "username": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "phone_number": random_phone_number(),
            "date_of_birth": random_birthday(is_student=True),
            "gender": self.gender,
            "password": "Testpassword@123",
            "scholarship": self.scholarship,
        }

    def tearDown(self):
        Student.objects.all().delete()
        super().tearDown()

    def test_create_student_with_valid_data(self):
        """
        Test creating a student with valid data.
        """

        form = StudentBaseForm(data=self.create_data)
        self.assertTrue(form.is_valid())

    def test_create_student_with_invalid_username(self):
        """
        Test creating a student with an invalid username.
        """

        username = "Invalid Username"
        user = UserFactory(username=username)
        StudentFactory(user=user)

        self.create_data["username"] = username
        form = StudentBaseForm(data=self.create_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_create_student_with_invalid_email(self):
        """
        Test creating a student with an invalid email.
        """

        email = "invalid.email@example.com"
        user = UserFactory(email=email)
        StudentFactory(user=user)

        self.create_data["email"] = email
        form = StudentBaseForm(data=self.create_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_invalid_phone_number(self):
        """
        Test form validation for an invalid phone number.
        """

        self.create_data["phone_number"] = "invalid_phone"

        form = StudentBaseForm(data=self.create_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(
            form.errors["phone_number"][0], ErrorMessage.PHONE_NUMBER_ONLY_NUMBER
        )

    def test_invalid_date_of_birth(self):
        """
        Test form validation for an invalid date of birth.
        """
        self.create_data["date_of_birth"] = "2025-01-01"

        form = StudentBaseForm(data=self.create_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertEqual(
            form.errors["date_of_birth"][0], ErrorMessage.INVALID_DATE_OF_BIRTH
        )

    def test_invalid_password(self):
        """
        Test form validation for an invalid password.
        """
        self.create_data["password"] = "1234567890"

        form = StudentBaseForm(data=self.create_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"][0], ErrorMessage.PASSWORD_LOWERCASE)


class StudentEditFormTest(TestCase):
    """
    Test case for the StudentEditForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        self.gender = random.choice([gender.value for gender in Gender])
        self.scholarship = random.choice(
            [scholarship.value for scholarship in ScholarshipChoices]
        )
        self.student = StudentFactory()
        self.update_data = {
            "first_name": fake.first_name(),
            "last_name": fake.first_name(),
            "phone_number": random_phone_number(),
            "date_of_birth": random_birthday(is_student=True),
            "gender": self.gender,
            "password": "Newpassword@123",
            "scholarship": self.scholarship,
        }

    def test_edit_student_with_valid_data(self):
        """
        Test editing a student with valid data.
        """

        form = StudentEditForm(instance=self.student, data=self.update_data)
        self.assertTrue(form.is_valid())

    def test_edit_student_with_invalid_phone_number(self):
        """
        Test editing a student with an invalid phone number.
        """

        self.update_data["phone_number"] = "48789645468764564678"
        form = StudentEditForm(instance=self.student, data=self.update_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(
            form.errors["phone_number"][0], ErrorMessage.PHONE_NUMBER_INVALID_LENGTH
        )

    def test_edit_student_with_invalid_date_of_birth(self):
        """
        Test editing a student with an invalid date of birth.
        """

        self.update_data["date_of_birth"] = "2025-01-01"
        form = StudentEditForm(instance=self.student, data=self.update_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertEqual(
            form.errors["date_of_birth"][0], ErrorMessage.INVALID_DATE_OF_BIRTH
        )

    def test_edit_student_with_invalid_password(self):
        """
        Test editing a student with an invalid password.
        """

        self.update_data["password"] = "123456789"
        form = StudentEditForm(instance=self.student, data=self.update_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"][0], ErrorMessage.PASSWORD_LOWERCASE)

    def test_edit_student_with_invalid_scholarship(self):
        """
        Test editing a student with an invalid scholarship.
        """

        self.update_data["scholarship"] = 150
        form = StudentEditForm(instance=self.student, data=self.update_data)
        self.assertFalse(form.is_valid())
        self.assertIn("scholarship", form.errors)
        self.assertEqual(
            form.errors["scholarship"][0],
            "Select a valid choice. 150 is not one of the available choices.",
        )
