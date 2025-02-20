from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from core.constants import Gender, Role


class UserManager(BaseUserManager):
    """
    Custom user manager for handling user creation and superuser creation.

    Methods:
        create_user: Creates and saves a regular user with the given email and password.
        create_superuser: Creates and saves a superuser with the given email and password.
    """

    def create_user(
        self,
        username,
        first_name,
        last_name,
        email,
        password=None,
        phone_number=None,
        date_of_birth=None,
        gender=Gender.MALE.value,
        **extra_fields,
    ):
        """
        Creates and saves a regular user with the given email and password.

        Args:
            username (str): The username of the user.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            email (str): The email of the user.
            password (str, optional): The password of the user. Defaults to None.
            phone_number (str, optional): The phone number of the user. Defaults to None.
            date_of_birth (date, optional): The birth date of the user. Defaults to None.
            gender (str, optional): The gender of the user. Defaults to Gender.MALE.value.
            **extra_fields: Additional fields for the user.

        Returns:
            User: The created user.
        """
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            gender=gender,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username,
        first_name,
        last_name,
        email,
        password=None,
        phone_number=None,
        date_of_birth=None,
        gender=Gender.MALE.value,
        **extra_fields,
    ):
        """
        Creates and saves a superuser with the given email and password.

        Args:
            username (str): The username of the superuser.
            first_name (str): The first name of the superuser.
            last_name (str): The last name of the superuser.
            email (str): The email of the superuser.
            password (str, optional): The password of the superuser. Defaults to None.
            phone_number (str, optional): The phone number of the superuser. Defaults to None.
            date_of_birth (date, optional): The birth date of the superuser. Defaults to None.
            gender (str, optional): The gender of the superuser. Defaults to Gender.MALE.value.
            **extra_fields: Additional fields for the superuser.

        Returns:
            User: The created superuser.
        """
        user = self.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            gender=gender,
            **extra_fields,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """
    Custom user model.

    Attributes:
        phone_number (CharField): The phone number of the user.
        date_of_birth (DateField): The birth date of the user.
        gender (CharField): The gender of the user.
        role (CharField): The role of the user (Instructor or Student).
    """

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        choices=Gender.choices(),
        help_text="Male or Female",
        max_length=6,
    )
    role = models.CharField(
        null=True,
        editable=False,
        choices=Role.choices(),
        help_text="Instructor or Student",
        max_length=10,
    )

    objects = UserManager()
