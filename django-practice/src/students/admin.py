from django.contrib import admin

from .forms import StudentCreationForm, StudentEditForm
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Student model.

    Displays user-related fields in the admin interface and handles the creation of a user when creating a student.
    """

    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "gender",
        "scholarship",
    ]

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns the appropriate form for creating or editing a student.

        Args:
            request (HttpRequest): The current request object.
            obj (Student, optional): The student instance being edited. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            ModelForm: The form instance to be used in the admin interface.
        """

        if obj is None:
            kwargs["form"] = StudentCreationForm
        else:
            kwargs["form"] = StudentEditForm
        return super().get_form(request, obj, **kwargs)

    def username(self, obj):
        """
        Returns the username of the user associated with the student.
        """

        return obj.user.username

    def first_name(self, obj):
        """
        Returns the first name of the user associated with the student.
        """

        return obj.user.first_name

    def last_name(self, obj):
        """
        Returns the last name of the user associated with the student.
        """

        return obj.user.last_name

    def email(self, obj):
        """
        Returns the email of the user associated with the student.
        """

        return obj.user.username

    def phone_number(self, obj):
        """
        Returns the phone number of the user associated with the student.
        """

        return obj.user.phone_number

    def date_of_birth(self, obj):
        """
        Returns the date of birth of the user associated with the student.
        """

        return obj.user.date_of_birth

    def gender(self, obj):
        """
        Returns the gender of the user associated with the student.
        """

        return obj.user.gender
