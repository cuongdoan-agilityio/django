from django.contrib import admin

from .models import Enrollment
from .forms import EnrollmentForm


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Enrollment model.

    This class defines how the Enrollment model is displayed and managed
    within the Django admin interface. It provides features for listing,
    filtering, searching, and using a custom form for Enrollment instances.

    Attributes:
        list_display (list): A list of model fields to be displayed in the
            admin list view.
        list_filter (list): A list of model fields that can be used to filter
            the admin list view.
        search_fields (list): A list of model fields that can be searched
            through the admin search functionality.
        form (Form): A custom form class used for creating and updating
            Enrollment instances.
    """

    list_display = [
        "course__title",
        "student__user__username",
        "created",
    ]
    list_filter = ["course__title"]
    search_fields = [
        "course__title",
        "student__user__username",
        "created",
    ]

    form = EnrollmentForm

    def get_readonly_fields(self, request, obj=None):
        """
        Returns a list of fields to be set as read-only in the admin form.
        """

        return ["course", "student", "created"] if obj else []

    def get_queryset(self, request):
        """
        Returns the queryset of Enrollment instances to be displayed in the admin list view.
        """

        queryset = super().get_queryset(request)
        return queryset.select_related("course", "student__user")
