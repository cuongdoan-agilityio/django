from django.contrib import admin

from core.filters import GenderFilter

from .forms import StudentCreationForm, StudentEditForm
from .models import Student


class ScholarshipFilter(admin.SimpleListFilter):
    """
    Custom filter for the scholarship field in the Student model.

    This filter allows the admin to filter students based on their scholarship status.

    Attributes:
        title (str): The title of the filter displayed in the admin interface.
        parameter_name (str): The URL parameter used for the filter.
    """

    title = "Scholarship"
    parameter_name = "scholarship"  # url parameter

    def lookups(self, request, model_admin):
        """
        Returns the list of filter options.

        Args:
            request (HttpRequest): The current request object.
            model_admin (ModelAdmin): The current model admin instance.

        Returns:
            list: A list of tuples containing the filter options.
        """

        return [
            ("no_scholarship", "No scholarship"),
            (25, "25%"),
            (50, "50%"),
            (75, "75%"),
            (100, "100%"),
            ("has_scholarship", "Has scholarship"),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the selected filter option.

        Args:
            request (HttpRequest): The current request object.
            queryset (QuerySet): The original queryset.

        Returns:
            QuerySet: The filtered queryset.
        """

        if not self.value():
            return queryset
        if self.value() == "no_scholarship":
            return queryset.filter(scholarship=0)
        if self.value() == "has_scholarship":
            return queryset.exclude(scholarship=0)
        return queryset.filter(scholarship=self.value())


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Student model.

    Displays user-related fields in the admin interface and handles the creation of a user when creating a student.
    """

    list_display = [
        "uuid",
        "username",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "gender",
        "scholarship",
        "modified",
    ]

    list_filter = [GenderFilter, ScholarshipFilter]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__phone_number",
        "user__email",
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user")

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

        return obj.user.email

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
