import datetime

from django import forms
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from courses.models import Course
from core.constants import Gender, Role, Degree, Status
from core.validators import (
    validate_password,
    validate_email,
    validate_username,
    validate_phone_number,
)
from .models import Instructor, Subject


User = get_user_model()


class InstructorBaseForm(forms.ModelForm):
    """
    Base form for instructor-related forms, including fields for creating or editing a user.

    Fields:
        username (CharField): The username of the user.
        first_name (CharField): The first name of the user.
        last_name (CharField): The last name of the user.
        email (EmailField): The email of the user.
        phone_number (CharField): The phone number of the user.
        date_of_birth (DateField): The birth date of the user.
        gender (ChoiceField): The gender of the user.
        password (CharField): The password of the user.
        subjects (ModelMultipleChoiceField): The subjects that the instructor specializes in.
        degree (ChoiceField): The degree of the instructor.
    """

    username = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    phone_number = forms.CharField(required=False)
    date_of_birth = forms.DateField(required=False)
    gender = forms.ChoiceField(choices=Gender.choices(), required=False)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=128)
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    degree = forms.ChoiceField(choices=Degree.choices())

    class Meta:
        model = Instructor
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
            "password",
            "subjects",
            "degree",
        )

    def clean_phone_number(self):
        """
        Validate the phone number to ensure it contains only digits and is of valid length.
        """

        phone = self.cleaned_data.get("phone_number")

        return validate_phone_number(phone)

    def clean_date_of_birth(self):
        """
        Validate the date of birth to ensure it represents a valid age.
        """

        dob = self.cleaned_data.get("date_of_birth")

        if not dob:
            return

        today = datetime.date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # From 18 years of age and older, individuals are fully responsible for the content posted on the internet.
        if age < 18 or age > 100:
            raise ValidationError("Invalid date of birth.")
        return dob

    def clean_password(self):
        """
        Validate the password to ensure it meets complexity requirements.
        """

        password = self.cleaned_data.get("password")

        return validate_password(password)


class InstructorCreationForm(InstructorBaseForm):
    """
    A form for creating new instructors, including fields for creating a new user.

    Methods:
        save: Saves the instructor and creates a new user with the provided data.
    """

    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.filter(
            instructor__isnull=True, status=Status.ACTIVATE.value
        ),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select courses to assign to this instructor.",
    )

    def save(self, commit=True):
        """
        Saves the instructor and creates a new user with the provided data.

        Args:
            commit (bool): Whether to save the instructor instance. Defaults to True.

        Returns:
            Instructor: The created instructor instance.
        """

        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"],
            phone_number=self.cleaned_data["phone_number"],
            date_of_birth=self.cleaned_data["date_of_birth"],
            gender=self.cleaned_data["gender"],
            role=Role.INSTRUCTOR.value,
            password=self.cleaned_data["password"],
        )
        instructor = super().save(commit=False)
        instructor.user = user
        instructor.courses.set(self.cleaned_data["courses"])

        if commit:
            instructor.save()
        return instructor

    def clean_username(self):
        """
        Validate that the username is unique.
        """

        username = self.cleaned_data.get("username")

        return validate_username(username)

    def clean_email(self):
        """
        Validate that the email is unique.
        """

        email = self.cleaned_data.get("email")

        return validate_email(email)


class InstructorEditForm(InstructorBaseForm):
    """
    A form for editing existing instructors, including fields for editing the associated user.

    Fields:
        username (CharField): The username of the user.
        first_name (CharField): The first name of the user.
        last_name (CharField): The last name of the user.
        email (EmailField): The email of the user.
        phone_number (CharField): The phone number of the user.
        date_of_birth (DateField): The birth date of the user.
        gender (ChoiceField): The gender of the user.
        password (CharField): The password of the user.
        subjects (ModelMultipleChoiceField): The subjects that the instructor specializes in.
        degree (ChoiceField): The degree of the instructor.
    """

    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select courses to assign to this instructor.",
    )
    username = forms.CharField(disabled=True)
    email = forms.EmailField(
        disabled=True,
        required=False,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "********", "autocomplete": "new-password"}
        ),
        min_length=8,
        max_length=128,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with the instance data.
        """

        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["username"].initial = self.instance.user.username
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email
            self.fields["phone_number"].initial = self.instance.user.phone_number
            self.fields["date_of_birth"].initial = self.instance.user.date_of_birth
            self.fields["gender"].initial = self.instance.user.gender
            self.fields["courses"].queryset = Course.objects.filter(
                Q(instructor=self.instance)
                | (Q(status=Status.ACTIVATE.value) and Q(instructor__isnull=True))
            )
            self.fields["courses"].initial = self.instance.courses.all

    def save(self, commit=True):
        """
        Save the instructor and update the associated user with the provided data.

        Args:
            commit (bool): Whether to save the instructor instance. Defaults to True.

        Returns:
            Instructor: The updated instructor instance.
        """

        instructor = super().save(commit=False)
        user = instructor.user

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.gender = self.cleaned_data["gender"]

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        user.save()
        instructor.courses.set(self.cleaned_data["courses"])

        if commit:
            instructor.save()

        return instructor
