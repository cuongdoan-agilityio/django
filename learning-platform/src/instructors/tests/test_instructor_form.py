from django.test import TestCase
import random
from faker import Faker

from accounts.factories import UserFactory
from core.constants import Gender, Degree
from instructors.forms import InstructorBaseForm, InstructorEditForm
from instructors.factories import InstructorFactory, SubjectFactory
from utils.helpers import random_birthday, random_phone_number
from core.exceptions import ErrorMessage


fake = Faker()


class InstructorBaseFormTest(TestCase):
    """
    Test case for the InstructorBaseForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        self.subject = SubjectFactory()
        self.gender = random.choice([gender.value for gender in Gender])
        self.create_data = {
            "username": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "phone_number": random_phone_number(),
            "date_of_birth": random_birthday(is_student=False),
            "gender": self.gender,
            "password": "Testpassword@123",
            "subjects": [str(self.subject.uuid)],
            "degree": "bachelor",
        }

    def test_create_instructor_with_valid_data(self):
        """
        Test creating an instructor with valid data.
        """

        form = InstructorBaseForm(data=self.create_data)
        self.assertTrue(form.is_valid())

    def test_create_instructor_invalid_username(self):
        """
        Test creating an instructor with an existing username.
        """

        username = "Existing User"
        user = UserFactory(username=username)
        InstructorFactory(user=user)

        self.create_data["username"] = username
        form = InstructorBaseForm(data=self.create_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_create_instructor_invalid_email(self):
        """
        Test creating an instructor with an existing email.
        """

        email = "invalid.email@example.com"
        user = UserFactory(email=email)
        InstructorFactory(user=user)
        self.create_data["email"] = email
        form = InstructorBaseForm(data=self.create_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_invalid_phone_number(self):
        """
        Test form validation for an invalid phone number.
        """

        self.create_data["phone_number"] = "invalid_phone"

        form = InstructorBaseForm(data=self.create_data)
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

        form = InstructorBaseForm(data=self.create_data)
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

        form = InstructorBaseForm(data=self.create_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"][0], ErrorMessage.PASSWORD_LOWERCASE)


class InstructorEditFormTest(TestCase):
    """
    Test case for the InstructorEditForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        self.instructor = InstructorFactory()
        subject = SubjectFactory()
        self.gender = random.choice([gender.value for gender in Gender])
        self.degree = random.choice([degree.value for degree in Degree])
        self.update_data = {
            "first_name": fake.first_name(),
            "last_name": fake.first_name(),
            "phone_number": random_phone_number(),
            "date_of_birth": random_birthday(is_student=False),
            "gender": self.gender,
            "password": "Newpassword@123",
            "subjects": [str(subject.uuid)],
            "degree": self.degree,
        }

    def test_edit_instructor_with_valid_data(self):
        """
        Test editing an instructor with valid data.
        """

        form = InstructorEditForm(instance=self.instructor, data=self.update_data)
        self.assertTrue(form.is_valid())

    def test_edit_instructor_with_invalid_phone_number(self):
        """
        Test editing a instructor with an invalid phone number.
        """

        self.update_data["phone_number"] = "123456789132456798"
        form = InstructorEditForm(instance=self.instructor, data=self.update_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(
            form.errors["phone_number"][0], ErrorMessage.PHONE_NUMBER_INVALID_LENGTH
        )

    def test_edit_instructor_with_invalid_date_of_birth(self):
        """
        Test editing a instructor with an invalid date of birth.
        """

        self.update_data["date_of_birth"] = "2010-01-10"
        form = InstructorEditForm(instance=self.instructor, data=self.update_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertEqual(
            form.errors["date_of_birth"][0], ErrorMessage.INVALID_DATE_OF_BIRTH
        )

    def test_edit_instructor_with_invalid_password(self):
        """
        Test editing a instructor with an invalid password.
        """

        self.update_data["password"] = "123456789"
        form = InstructorEditForm(instance=self.instructor, data=self.update_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"][0], ErrorMessage.PASSWORD_LOWERCASE)

    def test_edit_instructor_with_invalid_degree(self):
        """
        Test editing a instructor with an invalid degree.
        """

        self.update_data["degree"] = "invalid_degree"
        form = InstructorEditForm(instance=self.instructor, data=self.update_data)
        self.assertFalse(form.is_valid())
        self.assertIn("degree", form.errors)
        self.assertEqual(
            form.errors["degree"][0],
            "Select a valid choice. invalid_degree is not one of the available choices.",
        )
