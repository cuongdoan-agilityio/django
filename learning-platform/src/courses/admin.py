from django.contrib import admin

from core.constants import Status

from .models import Course


def activate_all(self, request, queryset):
    """
    Admin action to activate all selected courses.

    Args:
        self (ModelAdmin): The current ModelAdmin instance.
        request (HttpRequest): The current request object.
        queryset (QuerySet): The queryset of selected courses.
    """

    queryset.update(status=Status.ACTIVATE.value)
    message = "Activated all courses"
    self.message_user(request, message)


activate_all.short_description = "Activate all courses"


def deactivate_all(self, request, queryset):
    """
    Admin action to deactivate all selected courses.

    Args:
        self (ModelAdmin): The current ModelAdmin instance.
        request (HttpRequest): The current request object.
        queryset (QuerySet): The queryset of selected courses.
    """

    queryset.update(status=Status.INACTIVE.value)
    message = "Disabled all courses."
    self.message_user(request, message)


deactivate_all.short_description = "Disable all courses."


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Course model.

    This class defines how the Course model is displayed and managed
    within the Django admin interface. It provides features for listing,
    filtering, searching, and performing bulk actions on Course instances.

    Attributes:
        list_display (list): A list of fields to be displayed in the
            admin list view.
        list_filter (list): A list of fields that can be used to filter
            the admin list view.
        search_fields (list): A list of fields that can be searched.
        actions (list): A list of functions that can be executed as bulk
            actions on selected Course instances.
    """

    list_display = [
        "title",
        "description",
        "category",
        "instructor",
        "status",
    ]

    list_filter = ["title", "category__name", "instructor", "status"]
    search_fields = ["title", "category__name", "instructor__user__username"]

    actions = [activate_all, deactivate_all]
