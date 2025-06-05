from datetime import date
from copy import deepcopy

from accounts.forms import UserBaseForm, UserEditForm
from accounts.factories import UserFactory
from core.error_messages import ErrorMessage
from .base import BaseAccountModuleTestCase


class TestUserBaseForm(BaseAccountModuleTestCase):
    """
    Test case for the UserBaseForm.
    """

    def test_create_student_with_valid_data(self):
        """
        Test creating a student with valid data.
        """

        form = UserBaseForm(data=self.student_data)
        assert form.is_valid()

    def test_create_instructor_with_valid_data(self):
        """
        Test creating an instructor with valid data.
        """

        form = UserBaseForm(data=self.instructor_data)
        assert form.is_valid()

    def test_create_student_with_invalid_username(self):
        """
        Test creating a student with an invalid username.
        """

        invalid_username = "Invalid Username"
        UserFactory(username=invalid_username)

        self.student_data["username"] = invalid_username
        form = UserBaseForm(data=self.student_data)

        assert not form.is_valid()
        assert "username" in form.errors

    def test_create_instructor_invalid_username(self):
        """
        Test creating an instructor with an existing username.
        """

        invalid_username = "ExistingUsername"
        UserFactory(username=invalid_username)

        self.instructor_data["username"] = invalid_username
        form = UserBaseForm(data=self.instructor_data)

        assert not form.is_valid()
        assert "username" in form.errors

    def test_create_student_with_invalid_email(self):
        """
        Test creating a student with an invalid email.
        """

        invalid_email = "invalid.email@example.com"
        UserFactory(email=invalid_email)
        self.student_data["email"] = invalid_email
        form = UserBaseForm(data=self.student_data)

        assert not form.is_valid()
        assert "email" in form.errors

    def test_create_instructor_invalid_email(self):
        """
        Test creating an instructor with an existing email.
        """

        invalid_email = "existing@example.com"
        UserFactory(email=invalid_email)
        self.instructor_data["email"] = invalid_email
        form = UserBaseForm(data=self.instructor_data)

        assert not form.is_valid()
        assert "email" in form.errors

    def test_create_student_invalid_phone_number(self):
        """
        Test form validation for an invalid phone number.
        """

        self.student_data["phone_number"] = "invalid_phone"
        form = UserBaseForm(data=self.student_data)

        assert not form.is_valid()
        assert "phone_number" in form.errors
        assert form.errors["phone_number"][0] == ErrorMessage.PHONE_NUMBER_ONLY_NUMBER

    def test_create_instructor_invalid_phone_number(self):
        """
        Test form validation for an invalid phone number.
        """

        self.instructor_data["phone_number"] = "invalid_phone"
        form = UserBaseForm(data=self.instructor_data)

        assert not form.is_valid()
        assert "phone_number" in form.errors
        assert form.errors["phone_number"][0] == ErrorMessage.PHONE_NUMBER_ONLY_NUMBER

    def test_create_student_invalid_date_of_birth(self):
        """
        Test form validation for an invalid date of birth.
        """

        self.student_data["date_of_birth"] = date.today()
        form = UserBaseForm(data=self.student_data)

        assert not form.is_valid()
        assert "date_of_birth" in form.errors
        assert form.errors["date_of_birth"][0] == ErrorMessage.INVALID_DATE_OF_BIRTH

    def test_create_instructor_invalid_date_of_birth(self):
        """
        Test form validation for an invalid date of birth.
        """

        self.instructor_data["date_of_birth"] = date.today()
        form = UserBaseForm(data=self.instructor_data)

        assert not form.is_valid()
        assert "date_of_birth" in form.errors
        assert form.errors["date_of_birth"][0] == ErrorMessage.INVALID_DATE_OF_BIRTH

    def test_create_student_invalid_password(self):
        """
        Test form validation for an invalid password.
        """

        self.student_data["password"] = "1234567890"
        form = UserBaseForm(data=self.student_data)

        assert not form.is_valid()
        assert "password" in form.errors
        assert form.errors["password"][0] == ErrorMessage.PASSWORD_LOWERCASE

    def test_create_instructor_invalid_password(self):
        """
        Test form validation for an invalid password.
        """

        self.instructor_data["password"] = "1234567890"
        form = UserBaseForm(data=self.instructor_data)

        assert not form.is_valid()
        assert "password" in form.errors
        assert form.errors["password"][0] == ErrorMessage.PASSWORD_LOWERCASE


class TestStudentEditForm(BaseAccountModuleTestCase):
    """
    Test case for the StudentEditForm.
    """

    def test_edit_student_with_valid_data(self):
        """
        Test editing a student with valid data.
        """

        form = UserEditForm(instance=self.fake_student, data=self.student_data)
        assert form.is_valid()

    def test_edit_instructor_with_valid_data(self):
        """
        Test editing an instructor with valid data.
        """

        instructor_data = deepcopy(self.instructor_data)
        instructor_data.pop("email")
        form = UserEditForm(instance=self.fake_instructor, data=instructor_data)

        assert form.is_valid()

    def test_edit_student_with_invalid_phone_number(self):
        """
        Test editing a student with an invalid phone number.
        """

        self.student_data["phone_number"] = "48789645468764564678"
        form = UserEditForm(instance=self.fake_student, data=self.student_data)

        assert not form.is_valid()
        assert "phone_number" in form.errors
        assert (
            form.errors["phone_number"][0] == ErrorMessage.PHONE_NUMBER_INVALID_LENGTH
        )

    def test_edit_instructor_with_invalid_phone_number(self):
        """
        Test editing a instructor with an invalid phone number.
        """

        self.instructor_data["phone_number"] = "123456789132456798"
        form = UserEditForm(instance=self.fake_instructor, data=self.instructor_data)

        assert not form.is_valid()
        assert "phone_number" in form.errors
        assert (
            form.errors["phone_number"][0] == ErrorMessage.PHONE_NUMBER_INVALID_LENGTH
        )

    def test_edit_student_with_invalid_date_of_birth(self):
        """
        Test editing a student with an invalid date of birth.
        """

        self.student_data["date_of_birth"] = date.today()
        form = UserEditForm(instance=self.fake_student, data=self.student_data)

        assert not form.is_valid()
        assert "date_of_birth" in form.errors
        assert form.errors["date_of_birth"][0] == ErrorMessage.INVALID_DATE_OF_BIRTH

    def test_edit_instructor_with_invalid_date_of_birth(self):
        """
        Test editing a instructor with an invalid date of birth.
        """

        self.instructor_data["date_of_birth"] = date.today()
        form = UserEditForm(instance=self.fake_instructor, data=self.instructor_data)

        assert not form.is_valid()
        assert "date_of_birth" in form.errors
        assert form.errors["date_of_birth"][0] == ErrorMessage.INVALID_DATE_OF_BIRTH

    def test_edit_student_with_invalid_password(self):
        """
        Test editing a student with an invalid password.
        """

        self.student_data["password"] = "123456789"
        form = UserEditForm(instance=self.fake_student, data=self.student_data)

        assert not form.is_valid()
        assert "password" in form.errors
        assert form.errors["password"][0] == ErrorMessage.PASSWORD_LOWERCASE

    def test_edit_instructor_with_invalid_password(self):
        """
        Test editing a instructor with an invalid password.
        """

        self.instructor_data["password"] = "123456789"
        form = UserEditForm(instance=self.fake_instructor, data=self.instructor_data)

        assert not form.is_valid()
        assert "password" in form.errors
        assert form.errors["password"][0] == ErrorMessage.PASSWORD_LOWERCASE

    def test_edit_student_with_invalid_scholarship(self):
        """
        Test editing a student with an invalid scholarship.
        """

        self.student_data["scholarship"] = 150
        form = UserEditForm(instance=self.fake_student, data=self.student_data)

        assert not form.is_valid()
        assert "scholarship" in form.errors
        assert (
            form.errors["scholarship"][0]
            == "Select a valid choice. 150 is not one of the available choices."
        )

    def test_edit_instructor_with_invalid_degree(self):
        """
        Test editing a instructor with an invalid degree.
        """

        self.instructor_data["degree"] = "invalid_degree"
        form = UserEditForm(instance=self.fake_instructor, data=self.instructor_data)

        assert not form.is_valid()
        assert "degree" in form.errors
        assert (
            form.errors["degree"][0]
            == "Select a valid choice. invalid_degree is not one of the available choices."
        )
