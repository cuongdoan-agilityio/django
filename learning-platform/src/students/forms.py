from django import forms
from django.forms import BaseInlineFormSet
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from accounts.forms import UserBaseForm
from core.constants import ScholarshipChoices, Status
from core.exceptions import ErrorMessage

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
