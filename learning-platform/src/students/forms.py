import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.constants import Gender, Role, ScholarshipChoices, Status
from core.validators import (
    validate_password,
    validate_email,
    validate_username,
    validate_phone_number,
)
from core.exceptions import ErrorMessage
from courses.models import Course
from enrollments.models import Enrollment

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
        scholarship (ChoiceField): The scholarship amount for the student.
    """

    username = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    phone_number = forms.CharField(required=False)
    date_of_birth = forms.DateField(required=False)
    gender = forms.ChoiceField(choices=Gender.choices(), required=False)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, max_length=128)
    scholarship = forms.ChoiceField(
        choices=ScholarshipChoices.choices(), required=False
    )
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.filter(
            instructor__isnull=False, status=Status.ACTIVATE.value
        ),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select courses to assign to this instructor.",
    )

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
            "scholarship",
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
        if age < 6 or age > 100:
            raise ValidationError(ErrorMessage.INVALID_DATE_OF_BIRTH)
        return dob

    def clean_password(self):
        """
        Validate the password to ensure it meets complexity requirements.
        """

        password = self.cleaned_data.get("password")

        return validate_password(password)


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

        if courses := self.cleaned_data.get("courses"):
            for course in courses:
                Enrollment.objects.create(student=student, course=course)

        if commit:
            student.save()
        return student

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
    email = forms.EmailField(
        disabled=True,
        required=False,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "********"}),
        min_length=8,
        max_length=128,
        required=False,
    )
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select courses to assign to this student.",
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
            self.fields["password"].initial = self.instance.user.password
            self.fields["courses"].queryset = Course.objects.filter(
                status=Status.ACTIVATE.value, instructor__isnull=False
            )
            self.fields["courses"].initial = Course.objects.filter(
                enrollments__student=self.instance
            ).distinct()

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
        user.phone_number = self.cleaned_data["phone_number"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.gender = self.cleaned_data["gender"]

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        user.save()
        courses = self.cleaned_data.get("courses")
        if courses:
            for course in courses:
                if not Enrollment.objects.filter(student=student, course=course):
                    Enrollment.objects.create(
                        student=student,
                        course=course,
                    )

        Enrollment.objects.filter(student=student).exclude(course__in=courses).delete()

        if commit:
            student.save()
        return student
