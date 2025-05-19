from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model


from accounts.models import Specialization
from accounts.forms import UserBaseForm, UserEditForm
from core.filters import GenderFilter
from core.constants import Role

User = get_user_model()


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Specialization model.

    This class defines how the Specialization model is displayed and managed
    within the Django admin interface. It provides features for listing
    and searching Specialization instances.

    Attributes:
        list_display (list): A list of model fields to be displayed in the
            admin list view.
        search_fields (list): A list of model fields that can be searched
            through the admin search functionality.
    """

    list_display = ["id", "name", "description", "modified"]

    search_fields = ["name"]
    list_per_page = settings.ADMIN_PAGE_SIZE
    ordering = ["name", "-modified"]


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


class RoleFilter(admin.SimpleListFilter):
    """
    Custom filter for the role field in the User model.

    This filter allows the admin to filter users based on their role.

    Attributes:
        title (str): The title of the filter displayed in the admin interface.
        parameter_name (str): The URL parameter used for the filter.
    """

    title = "Role"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        """
        Returns the list of filter options.

        Args:
            request (HttpRequest): The current request object.
            model_admin (ModelAdmin): The current model admin instance.

        Returns:
            list: A list of tuples containing the filter options.
        """

        return [(role.value, role.name) for role in Role]

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
        return queryset.filter(role=self.value())


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the User model.

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
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "gender",
        "scholarship",
        "get_specializations",
        "degree",
        "is_active",
        "modified",
    ]

    list_filter = [
        GenderFilter,
        ScholarshipFilter,
        RoleFilter,
        "degree",
        "specializations",
    ]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "email",
    ]
    ordering = ["username", "-modified"]
    autocomplete_fields = ["specializations"]
    list_per_page = settings.ADMIN_PAGE_SIZE

    def get_queryset(self, request):
        """
        Customize the queryset for the Instructor admin interface.
        """

        queryset = super().get_queryset(request)
        return queryset.prefetch_related("specializations")

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
            kwargs["form"] = UserBaseForm
        else:
            kwargs["form"] = UserEditForm
        return super().get_form(request, obj, **kwargs)
