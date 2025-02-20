from django import forms
from django.contrib.auth import get_user_model
from core.constants import Gender, Role
from .models import Student


User = get_user_model()


class StudentCreationForm(forms.ModelForm):
    """
    A form for creating new students, including fields for creating a new user.

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

    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.CharField()
    date_of_birth = forms.DateField()
    gender = forms.ChoiceField(choices=Gender.choices())
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Student
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

    def save(self, commit=True):
        """
        Saves the student and creates a new user with the provided data.

        Args:
            commit (bool): Whether to save the student instance. Defaults to True.

        Returns:
            Student: The created student instance.
        """

        user_data = {
            "username": self.cleaned_data["username"],
            "first_name": self.cleaned_data["first_name"],
            "last_name": self.cleaned_data["last_name"],
            "email": self.cleaned_data["email"],
            "phone_number": self.cleaned_data["phone_number"],
            "date_of_birth": self.cleaned_data["date_of_birth"],
            "gender": self.cleaned_data["gender"],
            "role": Role.STUDENT.value,
            "password": self.cleaned_data["password"],
        }
        user = User.objects.create_user(**user_data)
        student = super().save(commit=False)
        student.user = user
        if commit:
            student.save()
        return student
