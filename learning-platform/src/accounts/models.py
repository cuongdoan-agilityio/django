from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.core.validators import MinValueValidator, MaxValueValidator

from core.constants import Gender
from core.models import AbstractBaseModel
from core.constants import ScholarshipChoices
from core.constants import Degree
from core.error_messages import ErrorMessage
from instructors.models import Subject
from .validators import validate_phone_number, validate_password


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
        password,
        email,
        last_name=None,
        first_name=None,
        phone_number=None,
        date_of_birth=None,
        gender=None,
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
            raise ValueError(ErrorMessage.EMAIL_REQUIRED)

        if not password:
            raise ValueError(ErrorMessage.PASSWORD_REQUIRED)

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
        email,
        password,
        last_name=None,
        first_name=None,
        phone_number=None,
        date_of_birth=None,
        gender=None,
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


class User(AbstractUser, AbstractBaseModel):
    """
    Custom user model.

    Attributes:
        id (UUIDField): The UUID of the user.
        username (CharField): The username of the user.
        first_name (CharField): The first name of the user.
        last_name (CharField): The last name of the user.
        email (EmailField): The email of the user.
        phone_number (CharField): The phone number of the user.
        date_of_birth (DateField): The birth date of the user.
        gender (CharField): The gender of the user.
        is_active (BooleanField): Whether the user is active.
        is_staff (BooleanField): Whether the user is staff.
    """

    first_name = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    last_name = models.CharField(max_length=30, blank=True, null=True, db_index=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        db_index=True,
    )
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        choices=Gender.choices(),
        help_text="Male or Female",
        max_length=6,
        blank=True,
        null=True,
    )
    scholarship = models.IntegerField(
        choices=ScholarshipChoices.choices(),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="The scholarship amount for the student.",
        db_index=True,
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name="instructors",
        help_text="The subjects that the instructor specializes in.",
    )
    degree = models.CharField(
        choices=Degree.choices(),
        default=Degree.NO.value,
        help_text="The degree of the instructor.",
        max_length=9,
        db_index=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "password",
    ]

    def __str__(self):
        return self.email

    def clean(self):
        """
        Verify for phone_number and password fields.
        """

        super().clean()

        if self.phone_number:
            validate_phone_number(self.phone_number)

        if self.password:
            validate_password(self.password)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_instructor(self):
        """
        Checks if the user is an instructor.

        Returns:
            bool: True if the user is an instructor, False otherwise.
        """
        return hasattr(self, "instructor_profile")

    @property
    def is_student(self):
        """
        Checks if the user is an student.

        Returns:
            bool: True if the user is an student, False otherwise.
        """
        return hasattr(self, "student_profile")
