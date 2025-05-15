import pytest
from django.contrib.auth import get_user_model
from accounts.factories import UserFactory


User = get_user_model()


@pytest.mark.django_db
class TestUserManager:
    """
    Unit test for the custom user manager.
    """

    def test_create_user(
        self,
        user_data,
    ):
        """
        Test create user.
        """

        user = UserFactory(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
        )
        assert user.email == user_data["email"]
        assert user.check_password(user_data["password"])
        assert user.username == user_data["username"]

    def test_create_student_without_email(
        self,
        user_data,
        student_role,
        random_scholarship,
    ):
        """
        Test create a user without an email.
        """

        with pytest.raises(ValueError):
            UserFactory(
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=student_role,
                email="",
                password=user_data["password"],
                scholarship=random_scholarship,
            )

    def test_create_instructor_without_email(
        self,
        user_data,
        instructor_role,
        random_degree,
        fake_specialization,
    ):
        """
        Test create a user without an email.
        """

        with pytest.raises(ValueError):
            UserFactory(
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=instructor_role,
                email="",
                password=user_data["password"],
                degree=random_degree,
                specialization=fake_specialization,
            )

    def test_create_student_without_password(
        self,
        user_data,
        student_role,
        random_scholarship,
    ):
        """
        Test create a user without a password.
        """

        with pytest.raises(ValueError):
            UserFactory(
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                role=student_role,
                scholarship=random_scholarship,
                password="",
            )

    def test_create_instructor_without_password(
        self,
        user_data,
        instructor_role,
        random_degree,
        fake_specialization,
    ):
        """
        Test create a user without a password.
        """

        with pytest.raises(ValueError):
            UserFactory(
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                role=instructor_role,
                degree=random_degree,
                specialization=fake_specialization,
                password="",
            )

    def test_create_superuser(
        self,
        user_data,
        admin_role,
    ):
        """
        Test create a superuser.
        """

        superuser = User.objects.create_superuser(
            username=user_data["username"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            password=user_data["password"],
            phone_number=user_data["phone_number"],
            date_of_birth=user_data["date_of_birth"],
            gender=user_data["gender"],
        )

        assert superuser.email == user_data["email"]
        assert superuser.username == user_data["username"]
        assert superuser.is_staff
        assert superuser.is_superuser
        assert superuser.gender == user_data["gender"]
        assert superuser.first_name == user_data["first_name"]
        assert superuser.last_name == user_data["last_name"]
        assert superuser.role == admin_role


@pytest.mark.django_db
class TestUserModel:
    """
    Unit test for the custom user model.
    """

    def test_user_creation(
        self,
        user_data,
        student_role,
    ):
        """
        Test create a user with all fields.
        """
        new_user = UserFactory(
            username=user_data["username"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            password=user_data["password"],
            phone_number=user_data["phone_number"],
            date_of_birth=user_data["date_of_birth"],
            gender=user_data["gender"],
            role=student_role,
        )

        assert new_user.username == user_data["username"]
        assert new_user.first_name == user_data["first_name"]
        assert new_user.last_name == user_data["last_name"]
        assert new_user.email == user_data["email"]
        assert new_user.phone_number == user_data["phone_number"]
        assert new_user.date_of_birth == user_data["date_of_birth"]
        assert new_user.gender == user_data["gender"]
        assert new_user.role == student_role

    def test_user_str(
        self,
        user_data,
    ):
        """
        Test the string representation of the user.
        """

        new_user = UserFactory(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
        )
        assert str(new_user) == user_data["email"]
