from django.test import TestCase
from django.contrib.auth import get_user_model
from core.constants import Gender, Role
from accounts.factories import UserFactory


User = get_user_model()
username = "testuser"
first_name = "Test"
last_name = "User"
email = "test@example.com"
password = "password1234"
phone_number = "1234567890"
date_of_birth = "1990-01-01"
gender = Gender.MALE.value
role = Role.INSTRUCTOR.value


class UserManagerTests(TestCase):
    """
    Unit test for the custom user manager.
    """

    def test_create_user(self):
        """
        Test create user.
        """

        user = UserFactory(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            gender=gender,
        )

        # Create register token object.
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.gender, gender)

    def test_create_user_without_email(self):
        """
        Test create a user without an email.
        """

        with self.assertRaises(ValueError):
            UserFactory(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email="",
                password=password,
            )

    def test_create_user_without_password(self):
        """
        Test create a user without a password.
        """

        with self.assertRaises(ValueError):
            UserFactory(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password="",
            )

    def test_create_superuser(self):
        """
        Test create a superuser without an email.
        """

        superuser = User.objects.create_superuser(
            username="admin",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="admin1234",
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            gender=gender,
        )
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.check_password("admin1234"))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.gender, gender)


class UserModelTests(TestCase):
    """
    Unit test for the custom user model.
    """

    def test_user_creation(self):
        """
        Test create a user with all fields.
        """

        user = UserFactory(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            gender=gender,
            role=role,
        )
        self.assertEqual(user.username, username)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.email, email)
        self.assertEqual(user.phone_number, phone_number)
        self.assertEqual(user.date_of_birth, date_of_birth)
        self.assertEqual(user.gender, gender)
        self.assertEqual(user.role, role)

    def test_user_str(self):
        """
        Test the string representation of a user.
        """

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        self.assertEqual(str(user), email)
