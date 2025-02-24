from django.contrib import admin

from .models import Subject


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
