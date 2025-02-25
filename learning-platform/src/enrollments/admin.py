from django.contrib import admin

from .models import Enrollment
from .forms import EnrollmentForm


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """
    Admin interface options for the Enrollment model.

    Displays the course title, student first name, and enrollment date in the list view.
        Allows filtering by course title.
        Allows searching by course title, student first name, and enrollment date.
    """

    list_display = [
        "course__title",
        "student__user__first_name",
        "enrolled_at",
    ]
    list_filter = ["course__title"]
    search_fields = [
        "course__title",
        "student__user__first_name",
        "enrolled_at",
    ]

    form = EnrollmentForm
