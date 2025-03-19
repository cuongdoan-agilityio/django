from django import forms
from django.contrib.auth import get_user_model
from .models import Instructor
from accounts.forms import UserBaseForm

from core.validators import validate_date_of_birth
from django.forms import BaseInlineFormSet
from courses.models import Category


User = get_user_model()


class InstructorBaseForm(UserBaseForm):
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

    def clean_date_of_birth(self):
        """
        Validate the date of birth to ensure it represents a valid age.
        """

        dob = self.cleaned_data.get("date_of_birth")

        return validate_date_of_birth(dob)


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


class CourseInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_choices = [
            (category.uuid, str(category))
            for category in Category.objects.all().order_by("name")
        ]

    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)

        if "category" in form.fields:
            form.fields["category"].choices = [
                ("", "-----------")
            ] + self.category_choices
        return form
