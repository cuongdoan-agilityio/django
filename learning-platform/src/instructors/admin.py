from django.contrib import admin

from .models import Instructor, Subject
from .forms import InstructorCreationForm, InstructorEditForm


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """
    Admin interface options for the Subject model.

    Displays the name of the subject in the list view and allows searching by name.
    """

    list_display = [
        "name",
    ]

    search_fields = [
        "name",
    ]


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "gender",
        "salary",
        "get_specializations",
        "degree",
    ]

    list_filter = ["user__gender", "degree", "specialization"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__phone_number",
        "user__email",
    ]

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = InstructorCreationForm
        else:
            kwargs["form"] = InstructorEditForm
        return super().get_form(request, obj, **kwargs)

    def username(self, obj):
        """
        Returns the username of the user associated with the instructor.
        """

        return obj.user.username

    def first_name(self, obj):
        """
        Returns the first name of the user associated with the instructor.
        """

        return obj.user.first_name

    def last_name(self, obj):
        """
        Returns the last name of the user associated with the instructor.
        """

        return obj.user.last_name

    def email(self, obj):
        """
        Returns the email of the user associated with the instructor.
        """

        return obj.user.username

    def phone_number(self, obj):
        """
        Returns the phone number of the user associated with the instructor.
        """

        return obj.user.phone_number

    def date_of_birth(self, obj):
        """
        Returns the date of birth of the user associated with the instructor.
        """

        return obj.user.date_of_birth

    def gender(self, obj):
        """
        Returns the gender of the user associated with the instructor.
        """

        return obj.user.gender
