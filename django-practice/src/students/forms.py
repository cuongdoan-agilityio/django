from django import forms
from django.contrib.auth import get_user_model
from core.constants import Gender, Role
from .models import Student


User = get_user_model()


class StudentBaseForm(forms.ModelForm):
    """
    Base form for student-related forms, including fields for creating or editing a user.

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


class StudentCreationForm(StudentBaseForm):
    """
    A form for creating new students, including fields for creating a new user.

    Methods:
        save: Saves the student and creates a new user with the provided data.
    """

    def save(self, commit=True):
        """
        Saves the student and creates a new user with the provided data.

        Args:
            commit (bool): Whether to save the student instance. Defaults to True.

        Returns:
            Student: The created student instance.
        """

        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"],
            phone_number=self.cleaned_data["phone_number"],
            date_of_birth=self.cleaned_data["date_of_birth"],
            gender=self.cleaned_data["gender"],
            role=Role.STUDENT.value,
            password=self.cleaned_data["password"],
        )
        student = super().save(commit=False)
        student.user = user
        if commit:
            student.save()
        return student


class StudentEditForm(StudentBaseForm):
    """
    A form for editing existing students, including fields for editing the associated user.

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
    password = forms.CharField(widget=forms.PasswordInput, required=False)

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
            self.fields["password"].initial = self.instance.user.password

    def save(self, commit=True):
        """
        Save the student and update the associated user with the provided data.

        Args:
            commit (bool): Whether to save the student instance. Defaults to True.

        Returns:
            Student: The updated student instance.
        """

        student = super().save(commit=False)
        user = student.user

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.gender = self.cleaned_data["gender"]

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        user.save()

        if commit:
            student.save()
        return student
