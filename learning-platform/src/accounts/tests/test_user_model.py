from django.contrib.auth import get_user_model
from accounts.factories import UserFactory
from core.tests.base import BaseTestCase


User = get_user_model()


class UserManagerTests(BaseTestCase):
    """
    Unit test for the custom user manager.
    """

    def setUp(self):
        return super().setUp()

    def test_create_user(self):
        """
        Test create user.
        """

        self.assertEqual(self.user.email, self.email)
        self.assertTrue(self.user.check_password(self.password))
        self.assertEqual(self.user.username, self.username)

    def test_create_user_without_email(self):
        """
        Test create a user without an email.
        """

        with self.assertRaises(ValueError):
            UserFactory(
                username=self.fake.user_name(),
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                email="",
                password=self.password,
            )

    def test_create_user_without_password(self):
        """
        Test create a user without a password.
        """

        with self.assertRaises(ValueError):
            UserFactory(
                username=self.fake.user_name(),
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                email=self.fake.email(),
                password="",
            )

    def test_create_superuser(self):
        """
        Test create a superuser without an email.
        """

        username = self.fake.user_name()
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        email = self.fake.email()
        password = self.password
        phone_number = self.random_user_phone_number()
        date_of_birth = self.random_date_of_birth(is_student=False)
        gender = self.random_gender()

        superuser = User.objects.create_superuser(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            gender=gender,
        )

        self.assertEqual(superuser.email, email)
        self.assertEqual(superuser.username, username)
        self.assertTrue(superuser.check_password(password))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.gender, gender)
        self.assertEqual(superuser.first_name, first_name)
        self.assertEqual(superuser.last_name, last_name)


class UserModelTests(BaseTestCase):
    """
    Unit test for the custom user model.
    """

    def setUp(self):
        super().setUp()

        self.username = self.fake.user_name()
        self.first_name = self.fake.first_name()
        self.last_name = self.fake.last_name()
        self.email = self.fake.email()
        self.password = self.password
        self.phone_number = self.random_user_phone_number()
        self.date_of_birth = self.random_date_of_birth(is_student=False)
        self.gender = self.random_gender()

    def test_user_creation(self):
        """
        Test create a user with all fields.
        """

        user = UserFactory(
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            password=self.password,
            phone_number=self.phone_number,
            date_of_birth=self.date_of_birth,
            gender=self.gender,
        )
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.phone_number, self.phone_number)
        self.assertEqual(user.date_of_birth, self.date_of_birth)
        self.assertEqual(user.gender, self.gender)
        self.assertEqual(str(user), self.email)
