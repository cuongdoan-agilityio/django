from django.contrib import admin
from django.conf import settings

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin class for Profile model.
    """

    list_display = ("user", "hero_name", "power")
    list_per_page = settings.LIST_PER_PAGE
