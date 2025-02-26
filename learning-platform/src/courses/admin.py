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

    for course in queryset:
        course.status = Status.ACTIVATE.value
        course.save()

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

    for course in queryset:
        course.status = Status.INACTIVE.value
        course.save()

    message = "Disabled all courses."
    self.message_user(request, message)


deactivate_all.short_description = "Disable all courses."


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Admin interface options for the Course model.

    Displays the title, description, category, instructor, and status of the course in the list view.
    Allows filtering by title, category, instructor, and status.
    Allows searching by title, category, and instructor.
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
