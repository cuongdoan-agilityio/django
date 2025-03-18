from django.contrib import admin
from django.conf import settings

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

    list_display = ["uuid", "name", "description", "modified"]

    search_fields = ["name"]
    list_per_page = settings.ADMIN_PAGE_SIZE
    ordering = ["name", "modified"]


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
        "uuid",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone_number",
        "user__date_of_birth",
        "user__gender",
        "get_subjects",
        "degree",
        "modified",
    ]

    list_filter = [GenderFilter, "degree", "subjects"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__phone_number",
        "user__email",
    ]
    ordering = ["user__username", "-modified"]
    autocomplete_fields = ["subjects"]
    list_per_page = settings.ADMIN_PAGE_SIZE

    def get_form(self, request, obj=None, **kwargs):
        """
        Overrides the default get_form method to dynamically select the appropriate form for the Instructor admin page.
        """

        if obj is None:
            kwargs["form"] = InstructorCreationForm
        else:
            kwargs["form"] = InstructorEditForm
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        """
        Customize the queryset for the Instructor admin interface.
        """

        queryset = super().get_queryset(request)
        return queryset.select_related("user").prefetch_related("subjects")
