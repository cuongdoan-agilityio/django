from django.contrib import admin
from django.conf import settings

from core.constants import Status

from .models import Course, Category, Enrollment
from .forms import EnrollmentForm
from .constants import CourseAdminMessage


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

    @admin.action(description="Activate all selected courses.")
    def activate_all(self, request, queryset):
        """
        Admin action to activate all selected courses.

        Args:
            self (ModelAdmin): The current ModelAdmin instance.
            request (HttpRequest): The current request object.
            queryset (QuerySet): The queryset of selected courses.
        """

        queryset.update(status=Status.ACTIVATE.value)
        self.message_user(request, CourseAdminMessage.ACTIVATE_ALL)

    @admin.action(description="Deactivate all selected courses.")
    def deactivate_all(self, request, queryset):
        """
        Admin action to deactivate all selected courses.

        Args:
            self (ModelAdmin): The current ModelAdmin instance.
            request (HttpRequest): The current request object.
            queryset (QuerySet): The queryset of selected courses.
        """

        queryset.update(status=Status.INACTIVE.value)
        self.message_user(request, CourseAdminMessage.DEACTIVATE_ALL)

    def get_queryset(self, request):
        query_set = super().get_queryset(request)
        return query_set.select_related("category", "instructor", "instructor__user")

    list_display = [
        "uuid",
        "title",
        "description",
        "category",
        "instructor",
        "status",
        "modified",
        "image_url",
    ]
    list_per_page = settings.ADMIN_PAGE_SIZE
    list_filter = ["title", "category__name", "status"]
    search_fields = ["title", "category__name", "instructor__user__username"]
    ordering = ["title"]
    autocomplete_fields = ["category", "instructor"]

    actions = [activate_all, deactivate_all]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Category model.

    Attributes:
        list_display (list): A list of model fields to be displayed in the
            admin list view.
        search_fields (list): A list of model fields that can be searched
            through the admin search functionality.
    """

    list_display = ["uuid", "name", "description", "modified"]
    list_per_page = settings.ADMIN_PAGE_SIZE
    search_fields = ["name"]
    ordering = ["name"]


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
        "uuid",
        "course__title",
        "student__user__username",
        "modified",
    ]
    list_filter = ["course__title"]
    search_fields = [
        "course__title",
        "student__user__username",
    ]
    list_per_page = settings.ADMIN_PAGE_SIZE
    ordering = ["course__title"]
    form = EnrollmentForm
    autocomplete_fields = ["course", "student"]

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
