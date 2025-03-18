import datetime

from django import forms
from django.forms import BaseInlineFormSet
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from accounts.forms import UserBaseForm
from core.constants import ScholarshipChoices, Status
from core.validators import validate_email, validate_username
from core.exceptions import ErrorMessage
from courses.models import Enrollment

from .models import Student


User = get_user_model()


class StudentBaseForm(UserBaseForm):
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

    scholarship = forms.ChoiceField(
        choices=ScholarshipChoices.choices(), required=False
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
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "********",
                "autocomplete": "new-password",
            }
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


class EnrollmentInlineFormSet(BaseInlineFormSet):
    """
    A custom inline formset for managing enrollments in the admin interface.
    """

    def clean(self):
        """
        Validate the formset to ensure that:
            - A student is not enrolled in the same course multiple times.
            - The course being enrolled in is active and has an instructor.
        """

        super().clean()
        course_ids = []

        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                if course := form.cleaned_data.get("course"):
                    course_id = course.uuid
                    if course_id in course_ids:
                        raise ValidationError(
                            ErrorMessage.ENROLLED_SAME_COURSE.format(course=course)
                        )
                    if not course.instructor or (
                        course.status != Status.ACTIVATE.value
                    ):
                        raise ValidationError(
                            ErrorMessage.COURSE_NOT_AVAILABLE.format(course=course)
                        )

                    course_ids.append(course_id)
