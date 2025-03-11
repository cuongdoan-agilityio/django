from django.test import TestCase

from accounts.factories import UserFactory
from core.constants import Gender, Status
from courses.factories import CourseFactory
from instructors.forms import InstructorCreationForm, InstructorEditForm
from instructors.models import Instructor
from instructors.factories import InstructorFactory, SubjectFactory


class InstructorCreationFormTest(TestCase):
    """
    Test case for the InstructorCreationForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        self.course = CourseFactory(status=Status.ACTIVATE.value, instructor=None)
        self.subject = SubjectFactory()
        self.valid_data = {
            "username": "Test Instructor",
            "first_name": "Test",
            "last_name": "Instructor",
            "email": "testinstructor@example.com",
            "phone_number": "1234567890",
            "date_of_birth": "1980-01-01",
            "gender": Gender.MALE.value,
            "password": "Testpassword@123",
            "subjects": [str(self.subject.uuid)],
            "degree": "bachelor",
            "courses": [str(self.course.uuid)],
        }

    def test_create_instructor_ok(self):
        """
        Test creating an instructor with valid data.
        """

        form = InstructorCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        instructor = form.save()
        self.assertIsInstance(instructor, Instructor)

    def test_create_instructor_invalid_username(self):
        """
        Test creating an instructor with an existing username.
        """

        username = "Existing User"
        user = UserFactory(username=username)

        InstructorFactory(user=user)

        self.valid_data["username"] = username
        form = InstructorCreationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_create_instructor_invalid_email(self):
        """
        Test creating an instructor with an existing email.
        """

        email = "invalid.email@example.com"
        self.valid_data["email"] = email
        user = UserFactory(email=email)
        InstructorFactory(user=user)
        form = InstructorCreationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class InstructorEditFormTest(TestCase):
    """
    Test case for the InstructorEditForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        self.instructor = InstructorFactory()
        self.course = CourseFactory(status=Status.ACTIVATE.value, instructor=None)
        subject = SubjectFactory()
        self.valid_data = {
            "first_name": "Updated",
            "last_name": "Instructor",
            "phone_number": "0987654321",
            "date_of_birth": "1979-01-01",
            "gender": Gender.FEMALE.value,
            "password": "Newpassword@123",
            "subjects": [str(subject.uuid)],
            "degree": "master",
            "courses": [str(self.course.uuid)],
        }

    def test_edit_instructor_ok(self):
        """
        Test editing an instructor with valid data.
        """

        form = InstructorEditForm(instance=self.instructor, data=self.valid_data)
        self.assertTrue(form.is_valid())
        instructor = form.save()
        self.assertIsInstance(instructor, Instructor)
        self.assertEqual(instructor.user.first_name, self.valid_data.get("first_name"))
