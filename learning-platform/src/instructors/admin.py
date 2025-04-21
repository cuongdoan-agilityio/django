from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model

from core.filters import GenderFilter

from .models import Instructor

# from accounts.models import Subject
from .forms import InstructorBaseForm, InstructorEditForm


User = get_user_model()

# TODO: Need remove code.
# @admin.register(Subject)
# class SubjectAdmin(admin.ModelAdmin):
#     """
#     Admin configuration for the Subject model.

#     This class defines how the Subject model is displayed and managed
#     within the Django admin interface. It provides features for listing
#     and searching Subject instances.

#     Attributes:
#         list_display (list): A list of model fields to be displayed in the
#             admin list view.
#         search_fields (list): A list of model fields that can be searched
#             through the admin search functionality.
#     """

#     list_display = ["id", "name", "description", "modified"]

#     search_fields = ["name"]
#     list_per_page = settings.ADMIN_PAGE_SIZE
#     ordering = ["name", "-modified"]


# class CourseInline(admin.TabularInline):
#     """
#     Inline admin class for the Course model.

#     This allows managing Course directly from the Student admin interface.
#     """

#     model = Course
#     extra = 0
#     fields = ["title", "description", "category", "status", "image_url"]
#     readonly_fields = ["instructor"]
#     autocomplete_fields = ["category"]

#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related("category")


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
        "id",
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

    # inlines = [CourseInline]

    def get_form(self, request, obj=None, **kwargs):
        """
        Overrides the default get_form method to dynamically select the appropriate form for the Instructor admin page.
        """

        if obj is None:
            kwargs["form"] = InstructorBaseForm
        else:
            kwargs["form"] = InstructorEditForm
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        """
        Customize the queryset for the Instructor admin interface.
        """

        queryset = super().get_queryset(request)
        return queryset.select_related("user").prefetch_related("subjects")

    def save_model(self, request, obj, form, change):
        """
        Save the Instructor and update the associated user with the provided data.

        Returns:
            Instructor: The Instructor instance.
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
