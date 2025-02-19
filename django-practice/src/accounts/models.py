from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from enum import Enum


class Gender(Enum):
    """
    Gender class representing different genders for users.

    Attributes:
        MALE (str): Represents male gender.
        FEMALE (str): Represents female gender.
    """

    MALE = "male"
    FEMALE = "female"

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples containing the gender values and names.

        Returns:
            list: A list of tuples with gender values and names.
        """
        return [(key.value, key.name) for key in cls]


class Role(Enum):
    """
    Role class representing different roles for users.

    Attributes:
        STUDENT (str): Represents the student role.
        INSTRUCTOR (str): Represents the instructor role.
    """

    STUDENT = "student"
    INSTRUCTOR = "instructor"

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples containing the role values and names.

        Returns:
            list: A list of tuples with role values and names.
        """
        return [(key.value, key.name) for key in cls]


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
        email,
        password=None,
        phone_number=None,
        birth_date=None,
        gender=Gender.MALE.value,
        **extra_fields,
    ):
        """
        Creates and saves a regular user with the given email and password.

        Args:
            username (str): The username of the user.
            email (str): The email of the user.
            password (str, optional): The password of the user. Defaults to None.
            phone_number (str, optional): The phone number of the user. Defaults to None.
            birth_date (date, optional): The birth date of the user. Defaults to None.
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
            email=email,
            phone_number=phone_number,
            birth_date=birth_date,
            gender=gender,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username,
        email,
        password=None,
        phone_number=None,
        birth_date=None,
        gender=Gender.MALE.value,
        **extra_fields,
    ):
        """
        Creates and saves a superuser with the given email and password.

        Args:
            username (str): The username of the superuser.
            email (str): The email of the superuser.
            password (str, optional): The password of the superuser. Defaults to None.
            phone_number (str, optional): The phone number of the superuser. Defaults to None.
            birth_date (date, optional): The birth date of the superuser. Defaults to None.
            gender (str, optional): The gender of the superuser. Defaults to Gender.MALE.value.
            **extra_fields: Additional fields for the superuser.

        Returns:
            User: The created superuser.
        """
        user = self.create_user(
            username,
            email,
            password,
            phone_number=phone_number,
            birth_date=birth_date,
            gender=gender,
            **extra_fields,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
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
