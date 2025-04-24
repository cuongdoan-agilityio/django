from django import forms
from django.contrib.auth import get_user_model

from core.constants import Gender, ScholarshipChoices, Role
from accounts.validators import (
    validate_password,
    validate_phone_number,
    validate_date_of_birth,
)
from core.validators import validate_username, validate_email
from core.error_messages import ErrorMessage


User = get_user_model()


class UserBaseForm(forms.ModelForm):
    """
    A base form for creating and updating user accounts.

    Attributes:
        username (CharField): The username of the user (required, max length 100).
        first_name (CharField): The first name of the user (optional, max length 50).
        last_name (CharField): The last name of the user (optional, max length 50).
        email (EmailField): The email address of the user (required).
        phone_number (CharField): The phone number of the user (optional).
        date_of_birth (DateField): The date of birth of the user (optional).
        gender (ChoiceField): The gender of the user (optional, choices from Gender constants).
        password (CharField): The password for the user account (required, min length 8, max length 128).
    """

    username = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    phone_number = forms.CharField(required=False)
    date_of_birth = forms.DateField(required=False)
    gender = forms.ChoiceField(choices=Gender.choices(), required=False)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=128)
    role = forms.ChoiceField(choices=Role.choices(), required=True)
    scholarship = forms.ChoiceField(
        choices=ScholarshipChoices.choices(), required=False
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
            "password",
            "role",
            "scholarship",
            "specializations",
            "degree",
        )

    def clean_phone_number(self):
        """
        Validate the phone number to ensure it contains only digits and is of valid length.
        """

        phone = self.cleaned_data.get("phone_number")

        return validate_phone_number(phone)

    def clean_password(self):
        """
        Validate the password to ensure it meets complexity requirements.
        """

        password = self.cleaned_data.get("password")

        return validate_password(password)

    def clean_date_of_birth(self):
        """
        Validate the date of birth to ensure it represents a valid age.
        """

        dob = self.cleaned_data.get("date_of_birth")

        return validate_date_of_birth(dob, is_student=True)

    def clean_username(self):
        """
        Validate that the username is unique.
        """

        username = self.cleaned_data.get("username")
        instance = getattr(self, "instance", None)
        if instance and instance._state.adding:
            return validate_username(username)

        return username

    def clean_email(self):
        """
        Validate that the email is unique.
        """

        email = self.cleaned_data.get("email")
        instance = getattr(self, "instance", None)
        if instance and instance._state.adding:
            return validate_email(email)

        return email

    def clean(self):
        if self.cleaned_data.get("role") == Role.STUDENT.value:
            if not self.cleaned_data.get("scholarship"):
                raise forms.ValidationError(ErrorMessage.SCHOLARSHIP_REQUIRED)
        if self.cleaned_data.get("role") == Role.INSTRUCTOR.value:
            if not self.cleaned_data.get("degree"):
                raise forms.ValidationError(ErrorMessage.DEGREE_REQUIRED)
            if not self.cleaned_data.get("specializations"):
                raise forms.ValidationError(ErrorMessage.SPECIALIZATION_REQUIRED)
        return super().clean()


class UserEditForm(UserBaseForm):
    """
    A form for editing existing user.

    Fields:
        username (CharField): The username of the user.
        first_name (CharField): The first name of the user.
        last_name (CharField): The last name of the user.
        email (EmailField): The email of the user.
        phone_number (CharField): The phone number of the user.
        date_of_birth (DateField): The birth date of the user.
        gender (ChoiceField): The gender of the user.
        password (CharField): The password of the user.
    """

    username = forms.CharField(disabled=True)
    email = forms.EmailField(
        disabled=True,
        required=False,
    )
    role = forms.ChoiceField(
        choices=Role.choices(),
        disabled=True,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "********",
                "autocomplete": "new-password",
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with the instance data.
        """

        super().__init__(*args, **kwargs)
        if self.instance and self.instance.is_student:
            self.fields["degree"].disabled = True
            self.fields["specializations"].disabled = True
        if self.instance and self.instance.is_instructor:
            self.fields["scholarship"].disabled = True
