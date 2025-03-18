from django import forms
from django.contrib.auth import get_user_model

from core.constants import Gender
from core.validators import validate_password, validate_phone_number


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
