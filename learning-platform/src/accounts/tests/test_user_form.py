import random
from copy import deepcopy
from accounts.forms import UserBaseForm, UserEditForm
from accounts.factories import UserFactory
from core.error_messages import ErrorMessage
from core.tests.base import BaseTestCase
from core.constants import Role, Gender


class UserBaseFormTest(BaseTestCase):
    """
    Test case for the StudentBaseForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """
        super().setUp()

        self.gender = self.random_gender()
        self.scholarship = self.random_scholarship()

        self.gender = random.choice([gender.value for gender in Gender])

        self.create_data = {
            "username": self.fake.user_name(),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "email": self.fake.email(),
            "phone_number": self.random_user_phone_number(),
            "date_of_birth": self.random_date_of_birth(is_student=True),
            "gender": self.gender,
            "password": "Testpassword@123",
        }

        self.student_data = {
            **self.create_data,
            "role": Role.STUDENT.value,
            "scholarship": self.scholarship,
        }

        self.instructor_data = {
            **self.create_data,
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "role": Role.INSTRUCTOR.value,
            "specializations": [str(self.specialization.id)],
            "degree": self.random_degree(),
        }

    def test_create_student_with_valid_data(self):
        """
        Test creating a student with valid data.
        """

        form = UserBaseForm(data=self.student_data)
        self.assertTrue(form.is_valid())

    def test_create_instructor_with_valid_data(self):
        """
        Test creating an instructor with valid data.
        """

        form = UserBaseForm(data=self.instructor_data)
        self.assertTrue(form.is_valid())

    def test_create_student_with_invalid_username(self):
        """
        Test creating a student with an invalid username.
        """

        username = "Invalid Username"
        UserFactory(username=username)

        self.student_data["username"] = username
        form = UserBaseForm(data=self.student_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_create_instructor_invalid_username(self):
        """
        Test creating an instructor with an existing username.
        """

        username = self.fake.user_name()
        UserFactory(username=username)

        self.instructor_data["username"] = username
        form = UserBaseForm(data=self.instructor_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_create_student_with_invalid_email(self):
        """
        Test creating a student with an invalid email.
        """

        email = "invalid.email@example.com"
        UserFactory(email=email)

        self.student_data["email"] = email
        form = UserBaseForm(data=self.student_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_create_instructor_invalid_email(self):
        """
        Test creating an instructor with an existing email.
        """

        email = self.fake.email()
        UserFactory(email=email)
        self.instructor_data["email"] = email
        form = UserBaseForm(data=self.instructor_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_create_student_invalid_phone_number(self):
        """
        Test form validation for an invalid phone number.
        """

        self.student_data["phone_number"] = "invalid_phone"

        form = UserBaseForm(data=self.student_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(
            form.errors["phone_number"][0], ErrorMessage.PHONE_NUMBER_ONLY_NUMBER
        )

    def test_create_instructor_invalid_phone_number(self):
        """
        Test form validation for an invalid phone number.
        """

        self.instructor_data["phone_number"] = "invalid_phone"

        form = UserBaseForm(data=self.instructor_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(
            form.errors["phone_number"][0], ErrorMessage.PHONE_NUMBER_ONLY_NUMBER
        )

    def test_create_student_invalid_date_of_birth(self):
        """
        Test form validation for an invalid date of birth.
        """
        self.student_data["date_of_birth"] = "2025-01-01"

        form = UserBaseForm(data=self.student_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertEqual(
            form.errors["date_of_birth"][0], ErrorMessage.INVALID_DATE_OF_BIRTH
        )

    def test_create_instructor_invalid_date_of_birth(self):
        """
        Test form validation for an invalid date of birth.
        """
        self.instructor_data["date_of_birth"] = "2025-01-01"

        form = UserBaseForm(data=self.instructor_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertEqual(
            form.errors["date_of_birth"][0], ErrorMessage.INVALID_DATE_OF_BIRTH
        )

    def test_create_student_invalid_password(self):
        """
        Test form validation for an invalid password.
        """
        self.student_data["password"] = "1234567890"

        form = UserBaseForm(data=self.student_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"][0], ErrorMessage.PASSWORD_LOWERCASE)

    def test_create_instructor_invalid_password(self):
        """
        Test form validation for an invalid password.
        """
        self.instructor_data["password"] = "1234567890"

        form = UserBaseForm(data=self.instructor_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"][0], ErrorMessage.PASSWORD_LOWERCASE)


class StudentEditFormTest(BaseTestCase):
    """
    Test case for the StudentEditForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        super().setUp()

        self.gender = self.random_gender()
        self.scholarship = self.random_scholarship()
        self.student = UserFactory(role=Role.STUDENT.value)
        self.instructor = UserFactory(role=Role.INSTRUCTOR.value)
        self.update_data = {
            "first_name": self.fake.first_name(),
            "last_name": self.fake.first_name(),
            "phone_number": self.random_user_phone_number(),
            "date_of_birth": self.random_date_of_birth(is_student=True),
            "gender": self.gender,
            "password": "Newpassword@123",
        }

        self.student_data = {
            **self.update_data,
            "scholarship": self.scholarship,
        }

        self.instructor_data = {
            **self.update_data,
            "email": self.fake.email(),
            "specializations": [str(self.specialization.id)],
            "degree": self.random_degree(),
        }

    def test_edit_student_with_valid_data(self):
        """
        Test editing a student with valid data.
        """

        form = UserEditForm(instance=self.student, data=self.student_data)
        self.assertTrue(form.is_valid())

    def test_edit_instructor_with_valid_data(self):
        """
        Test editing an instructor with valid data.
        """

        instructor_data = deepcopy(self.instructor_data)
        instructor_data.pop("email")
        form = UserEditForm(instance=self.instructor, data=instructor_data)
        self.assertTrue(form.is_valid())

    def test_edit_student_with_invalid_phone_number(self):
        """
        Test editing a student with an invalid phone number.
        """

        self.student_data["phone_number"] = "48789645468764564678"
        form = UserEditForm(instance=self.student, data=self.student_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(
            form.errors["phone_number"][0], ErrorMessage.PHONE_NUMBER_INVALID_LENGTH
        )

    def test_edit_instructor_with_invalid_phone_number(self):
        """
        Test editing a instructor with an invalid phone number.
        """

        self.instructor_data["phone_number"] = "123456789132456798"
        form = UserEditForm(instance=self.instructor, data=self.instructor_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
        self.assertEqual(
            form.errors["phone_number"][0], ErrorMessage.PHONE_NUMBER_INVALID_LENGTH
        )

    def test_edit_student_with_invalid_date_of_birth(self):
        """
        Test editing a student with an invalid date of birth.
        """

        self.student_data["date_of_birth"] = "2025-01-01"
        form = UserEditForm(instance=self.student, data=self.student_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertEqual(
            form.errors["date_of_birth"][0], ErrorMessage.INVALID_DATE_OF_BIRTH
        )

    def test_edit_student_with_invalid_password(self):
        """
        Test editing a student with an invalid password.
        """

        self.student_data["password"] = "123456789"
        form = UserEditForm(instance=self.student, data=self.student_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"][0], ErrorMessage.PASSWORD_LOWERCASE)

    def test_edit_student_with_invalid_scholarship(self):
        """
        Test editing a student with an invalid scholarship.
        """

        self.student_data["scholarship"] = 150
        form = UserEditForm(instance=self.student, data=self.student_data)
        self.assertFalse(form.is_valid())
        self.assertIn("scholarship", form.errors)
        self.assertEqual(
            form.errors["scholarship"][0],
            "Select a valid choice. 150 is not one of the available choices.",
        )

    def test_edit_instructor_with_invalid_date_of_birth(self):
        """
        Test editing a instructor with an invalid date of birth.
        """

        self.instructor_data["date_of_birth"] = "2010-01-10"
        form = UserEditForm(instance=self.instructor, data=self.instructor_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertEqual(
            form.errors["date_of_birth"][0], ErrorMessage.INVALID_DATE_OF_BIRTH
        )

    def test_edit_instructor_with_invalid_password(self):
        """
        Test editing a instructor with an invalid password.
        """

        self.instructor_data["password"] = "123456789"
        form = UserEditForm(instance=self.instructor, data=self.instructor_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"][0], ErrorMessage.PASSWORD_LOWERCASE)

    def test_edit_instructor_with_invalid_degree(self):
        """
        Test editing a instructor with an invalid degree.
        """

        self.instructor_data["degree"] = "invalid_degree"
        form = UserEditForm(instance=self.instructor, data=self.instructor_data)
        self.assertFalse(form.is_valid())
        self.assertIn("degree", form.errors)
        self.assertEqual(
            form.errors["degree"][0],
            "Select a valid choice. invalid_degree is not one of the available choices.",
        )
