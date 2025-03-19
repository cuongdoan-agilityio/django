from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model

from core.filters import GenderFilter

from courses.models import Enrollment
from .forms import (
    StudentBaseForm,
    StudentEditForm,
    EnrollmentInlineFormSet,
)
from .models import Student

User = get_user_model()


class ScholarshipFilter(admin.SimpleListFilter):
    """
    Custom filter for the scholarship field in the Student model.

    This filter allows the admin to filter students based on their scholarship status.

    Attributes:
        title (str): The title of the filter displayed in the admin interface.
        parameter_name (str): The URL parameter used for the filter.
    """

    title = "Scholarship"
    parameter_name = "scholarship"

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


class EnrollmentInline(admin.TabularInline):
    """
    Inline admin class for the Enrollment model.

    This allows managing enrollments directly from the Student admin interface.
    """

    model = Enrollment
    extra = 0
    fields = ["course", "student"]
    readonly_fields = ["student"]
    formset = EnrollmentInlineFormSet

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course", "student__user")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Student model.

    Displays user-related fields in the admin interface and handles the creation of a user when creating a student.
    """

    list_display = [
        "uuid",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone_number",
        "user__date_of_birth",
        "user__gender",
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

    inlines = [EnrollmentInline]
    list_per_page = settings.ADMIN_PAGE_SIZE
    ordering = ["user__username", "modified"]

    def save_model(self, request, obj, form, change):
        """
        Save the student and update the associated user with the provided data.

        Returns:
            Student: The student instance.
        """

        cleaned_data = form.cleaned_data

        if change:
            user = obj.user
            user.first_name = cleaned_data["first_name"]
            user.last_name = cleaned_data["last_name"]
            user.phone_number = cleaned_data["phone_number"]
            user.date_of_birth = cleaned_data["date_of_birth"]
            user.gender = cleaned_data["gender"]

            password = cleaned_data.get("password")
            if password:
                user.set_password(password)

            user.save()
        else:
            user = User.objects.create_user(
                username=cleaned_data["username"],
                first_name=cleaned_data["first_name"],
                last_name=cleaned_data["last_name"],
                email=cleaned_data["email"],
                phone_number=cleaned_data["phone_number"],
                date_of_birth=cleaned_data["date_of_birth"],
                gender=cleaned_data["gender"],
                password=cleaned_data["password"],
            )
            obj.user = user

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        Customize the queryset for the Students admin interface.
        """

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
            kwargs["form"] = StudentBaseForm
        else:
            kwargs["form"] = StudentEditForm
        return super().get_form(request, obj, **kwargs)
