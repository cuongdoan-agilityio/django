from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model


from accounts.models import Subject
from core.filters import GenderFilter

User = get_user_model()


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

    list_display = ["id", "name", "description", "modified"]

    search_fields = ["name"]
    list_per_page = settings.ADMIN_PAGE_SIZE
    ordering = ["name", "-modified"]


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
    ]

    list_filter = [GenderFilter]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "email",
    ]
    ordering = ["username", "-modified"]
    list_per_page = settings.ADMIN_PAGE_SIZE
