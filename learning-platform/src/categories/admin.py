from django.contrib import admin

from .models import Category


@admin.register(Category)
class SubjectAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Category model.


    Attributes:
        list_display (list): A list of model fields to be displayed in the
            admin list view. In this case, only the 'name' field is shown.
        search_fields (list): A list of model fields that can be searched
            through the admin search functionality. Here, the 'name' field
            is used for searching.
    """

    list_display = [
        "name",
    ]

    search_fields = [
        "name",
    ]
