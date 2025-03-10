from django.test import TestCase
from students.forms import StudentCreationForm, StudentEditForm
from students.models import Student
from students.factories import StudentFactory
from accounts.factories import UserFactory
from courses.factories import CourseFactory
from core.constants import Gender, Status


class StudentCreationFormTest(TestCase):
    """
    Test case for the StudentCreationForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        self.course = CourseFactory(status=Status.ACTIVATE.value)
        self.valid_data = {
            "username": "Test User",
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "phone_number": "1234567890",
            "date_of_birth": "2000-01-01",
            "gender": Gender.MALE.value,
            "password": "Testpassword@123",
            "scholarship": 0,
            "courses": [self.course.uuid],
        }

    def tearDown(self):
        Student.objects.all().delete()
        super().tearDown()

    def test_create_student_ok(self):
        """
        Test creating a student with valid data.
        """

        student = StudentFactory()
        form = StudentCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        student = form.save()
        self.assertIsInstance(student, Student)

    def test_create_student_invalid_username(self):
        """
        Test creating a student with an invalid username.
        """

        username = "Invalid Username"
        user = UserFactory(username=username)
        StudentFactory(user=user)

        self.valid_data["username"] = username
        form = StudentCreationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_create_student_invalid_email(self):
        """
        Test creating a student with an invalid email.
        """

        email = "invalid.email@example.com"
        user = UserFactory(email=email)
        StudentFactory(user=user)

        self.valid_data["email"] = email
        form = StudentCreationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class StudentEditFormTest(TestCase):
    """
    Test case for the StudentEditForm.
    """

    def setUp(self):
        """
        Set up the test case with sample data.
        """

        self.student = StudentFactory()
        self.course = CourseFactory(status=Status.ACTIVATE.value)
        self.valid_data = {
            "first_name": "Updated",
            "last_name": "User",
            "phone_number": "0987654321",
            "date_of_birth": "1999-01-01",
            "gender": Gender.FEMALE.value,
            "password": "Newpassword@123",
            "courses": [self.course.uuid],
        }

    def test_edit_student_ok(self):
        """
        Test editing a student with valid data.
        """

        form = StudentEditForm(instance=self.student, data=self.valid_data)
        self.assertTrue(form.is_valid())
        student = form.save()
        self.assertIsInstance(student, Student)
        self.assertEqual(student.user.first_name, self.valid_data.get("first_name"))

    def test_edit_student_invalid_data(self):
        """
        Test editing a student with invalid data.
        """

        self.valid_data["phone_number"] = "03256984572158"
        form = StudentEditForm(instance=self.student, data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
