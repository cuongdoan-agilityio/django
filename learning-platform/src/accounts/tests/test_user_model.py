import pytest
from django.contrib.auth import get_user_model
from accounts.factories import UserFactory
from .base import BaseAccountModuleTestCase


User = get_user_model()


class TestUserManager(BaseAccountModuleTestCase):
    """
    Unit test for the custom user manager.
    """

    def test_create_user(self):
        """
        Test create user.
        """

        user = UserFactory(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

        assert user.email == self.user_data["email"]
        assert user.check_password(self.user_data["password"])
        assert user.username == self.user_data["username"]

    def test_create_student_without_email(self):
        """
        Test create a user without an email.
        """

        with pytest.raises(ValueError):
            UserFactory(
                username=self.user_data["username"],
                first_name=self.user_data["first_name"],
                last_name=self.user_data["last_name"],
                role=self.student_role,
                email="",
                password=self.user_data["password"],
                scholarship=self.random_scholarship,
            )

    def test_create_instructor_without_email(self):
        """
        Test create a user without an email.
        """

        with pytest.raises(ValueError):
            UserFactory(
                username=self.user_data["username"],
                first_name=self.user_data["first_name"],
                last_name=self.user_data["last_name"],
                role=self.instructor_role,
                email="",
                password=self.user_data["password"],
                degree=self.random_degree,
                specialization=self.fake_specialization,
            )

    def test_create_student_without_password(self):
        """
        Test create a user without a password.
        """

        with pytest.raises(ValueError):
            UserFactory(
                username=self.user_data["username"],
                first_name=self.user_data["first_name"],
                last_name=self.user_data["last_name"],
                email=self.user_data["email"],
                role=self.student_role,
                scholarship=self.random_scholarship,
                password="",
            )

    def test_create_instructor_without_password(self):
        """
        Test create a user without a password.
        """

        with pytest.raises(ValueError):
            UserFactory(
                username=self.user_data["username"],
                first_name=self.user_data["first_name"],
                last_name=self.user_data["last_name"],
                email=self.user_data["email"],
                role=self.instructor_role,
                degree=self.random_degree,
                specialization=self.fake_specialization,
                password="",
            )

    def test_create_superuser(self):
        """
        Test create a superuser.
        """

        superuser = User.objects.create_superuser(
            username=self.user_data["username"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            phone_number=self.user_data["phone_number"],
            date_of_birth=self.user_data["date_of_birth"],
            gender=self.user_data["gender"],
        )

        assert superuser.email == self.user_data["email"]
        assert superuser.username == self.user_data["username"]
        assert superuser.is_staff
        assert superuser.is_superuser
        assert superuser.gender == self.user_data["gender"]
        assert superuser.first_name == self.user_data["first_name"]
        assert superuser.last_name == self.user_data["last_name"]
        assert superuser.role == self.admin_role


class TestUserModel(BaseAccountModuleTestCase):
    """
    Unit test for the custom user model.
    """

    def test_user_creation(self):
        """
        Test create a user with all fields.
        """
        new_user = UserFactory(
            username=self.user_data["username"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            phone_number=self.user_data["phone_number"],
            date_of_birth=self.user_data["date_of_birth"],
            gender=self.user_data["gender"],
            role=self.student_role,
        )

        assert new_user.username == self.user_data["username"]
        assert new_user.first_name == self.user_data["first_name"]
        assert new_user.last_name == self.user_data["last_name"]
        assert new_user.email == self.user_data["email"]
        assert new_user.phone_number == self.user_data["phone_number"]
        assert new_user.date_of_birth == self.user_data["date_of_birth"]
        assert new_user.gender == self.user_data["gender"]
        assert new_user.role == self.student_role

    def test_user_str(self):
        """
        Test the string representation of the user.
        """

        new_user = UserFactory(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )
        assert str(new_user) == self.user_data["email"]
