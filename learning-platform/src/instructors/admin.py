from django.contrib import admin

from core.filters import GenderFilter

from .models import Instructor, Subject
from .forms import InstructorCreationForm, InstructorEditForm


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Subject model.

    This class defines how the Subject model is displayed and managed
    within the Django admin interface. It provides features for listing
    and searching Subject instances.

    Attributes:
        list_display (list): A list of model fields to be displayed in the
            admin list view.
        search_fields (list): A list of model fields that can be searched
            through the admin search functionality.
    """

    list_display = ["name"]

    search_fields = ["name"]


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Instructor model.

    This class defines how the Instructor model is displayed and managed
    within the Django admin interface. It provides features for listing,
    filtering, searching, and using different forms for creating and
    editing Instructor instances.

    Attributes:
        list_display (list): A list of model fields to be displayed in the
            admin list view.
        list_filter (list): A list of model fields that can be used to filter
            the admin list view.
        search_fields (list): A list of model fields that can be searched
            through the admin search functionality.

    Methods:
        get_form(request, obj=None, **kwargs):
            Overrides the default get_form method to use different forms
            (InstructorCreationForm or InstructorEditForm) based on whether
            an Instructor instance is being created or edited.
    """

    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "gender",
        "get_subjects",
        "get_courses",
        "degree",
    ]

    list_filter = [GenderFilter, "degree", "subjects"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__phone_number",
        "user__email",
    ]

    def get_form(self, request, obj=None, **kwargs):
        """
        Overrides the default get_form method to dynamically select the appropriate form for the Instructor admin page.
        """

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

        return obj.user.email

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
