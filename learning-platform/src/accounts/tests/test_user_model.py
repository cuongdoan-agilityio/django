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

    def test_create_student_without_email(self):
        """
        Test create a user without an email.
        """

        with self.assertRaises(ValueError):
            UserFactory(
                username=self.fake.user_name(),
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                role=self.student_role,
                email="",
                password=self.password,
                scholarship=self.random_scholarship(),
            )

    def test_create_instructor_without_email(self):
        """
        Test create a user without an email.
        """

        with self.assertRaises(ValueError):
            UserFactory(
                username=self.fake.user_name(),
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                role=self.instructor_role,
                email="",
                password=self.password,
                degree=self.random_degree(),
                subject=self.subject,
            )

    def test_create_student_without_password(self):
        """
        Test create a user without a password.
        """

        with self.assertRaises(ValueError):
            UserFactory(
                username=self.fake.user_name(),
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                email=self.fake.email(),
                role=self.student_role,
                scholarship=self.random_scholarship(),
                password="",
            )

    def test_create_instructor_without_password(self):
        """
        Test create a user without a password.
        """

        with self.assertRaises(ValueError):
            UserFactory(
                username=self.fake.user_name(),
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                email=self.fake.email(),
                role=self.instructor_role,
                degree=self.random_degree(),
                subject=self.subject,
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
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.gender, gender)
        self.assertEqual(superuser.first_name, first_name)
        self.assertEqual(superuser.last_name, last_name)
        self.assertEqual(superuser.role, self.admin_role)


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

        self.new_user = UserFactory(
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            password=self.password,
            phone_number=self.phone_number,
            date_of_birth=self.date_of_birth,
            gender=self.gender,
            role=self.student_role,
        )

    def test_user_creation(self):
        """
        Test create a user with all fields.
        """

        self.assertEqual(self.new_user.username, self.username)
        self.assertEqual(self.new_user.first_name, self.first_name)
        self.assertEqual(self.new_user.last_name, self.last_name)
        self.assertEqual(self.new_user.email, self.email)
        self.assertEqual(self.new_user.phone_number, self.phone_number)
        self.assertEqual(self.new_user.date_of_birth, self.date_of_birth)
        self.assertEqual(self.new_user.gender, self.gender)
        self.assertEqual(self.new_user.role, self.student_role)

    def test_user_str(self):
        """
        Test the string representation of the user.
        """

        self.assertEqual(str(self.new_user), self.email)
