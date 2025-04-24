from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from core.constants import Gender, Role
from core.models import AbstractBaseModel
from core.constants import ScholarshipChoices
from core.constants import Degree
from core.error_messages import ErrorMessage
from .validators import validate_phone_number, validate_date_of_birth


class Specialization(AbstractBaseModel):
    """
    Subject model representing a subject that an instructor can specialize in.

    Attributes:
        name (CharField): The name of the subject.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(
        help_text="Subject description", blank=True, null=True
    )

    def __str__(self):
        return self.name


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
            password=password,
            **extra_fields,
        )
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
            role=Role.ADMIN.value,
            is_staff=True,
            is_superuser=True,
            **extra_fields,
        )
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

    first_name = models.CharField(
        help_text="First name", max_length=150, blank=True, null=True, db_index=True
    )
    last_name = models.CharField(
        help_text="Last name", max_length=150, blank=True, null=True, db_index=True
    )
    email = models.EmailField(help_text="email address", unique=True)
    phone_number = models.CharField(
        help_text="Phone number",
        max_length=11,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        db_index=True,
    )
    date_of_birth = models.DateField(
        help_text="Date of birth",
        blank=True,
        null=True,
        validators=[validate_date_of_birth],
    )
    gender = models.CharField(
        choices=Gender.choices(),
        help_text="Male or Female",
        max_length=6,
        blank=True,
        null=True,
    )
    scholarship = models.IntegerField(
        choices=ScholarshipChoices.choices(),
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="The scholarship amount for the student.",
        blank=True,
        null=True,
        db_index=True,
    )
    specializations = models.ManyToManyField(
        Specialization,
        related_name="user",
        help_text="The subjects that the instructor specializes in.",
        blank=True,
    )
    degree = models.CharField(
        choices=Degree.choices(),
        default=Degree.NO.value,
        help_text="The degree of the instructor.",
        max_length=9,
        db_index=True,
        null=True,
        blank=True,
    )

    role = models.CharField(
        choices=Role.choices(),
        default=Role.STUDENT.value,
        max_length=10,
        help_text="The role of the user.",
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
        Clean the user data before saving.
        """
        if self.role == Role.STUDENT.value:
            if self.scholarship not in ScholarshipChoices.values():
                raise ValidationError(ErrorMessage.REQUIRED_FIELD)
            self.degree = None
            self.specializations.clear()

        if self.role == Role.INSTRUCTOR.value:
            if self.degree not in Degree.values():
                raise ValidationError("Invalid degree.")
            self.scholarship = None

    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)

        if not self._state.adding and not self.password:
            user = User.objects.get(pk=self.pk)
            self.password = user.password

        super().save(*args, **kwargs)

    def get_specializations(self):
        return ", ".join([spec.name for spec in self.specializations.all()])

    @property
    def is_instructor(self):
        """
        Checks if the user is an instructor.

        Returns:
            bool: True if the user is an instructor, False otherwise.
        """
        return self.role == Role.INSTRUCTOR.value

    @property
    def is_student(self):
        """
        Checks if the user is an student.

        Returns:
            bool: True if the user is an student, False otherwise.
        """
        return self.role == Role.STUDENT.value
