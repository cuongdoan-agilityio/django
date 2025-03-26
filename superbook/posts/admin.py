from django.contrib import admin
from django.conf import settings

from .models.post import Post
from .models.superhero import SuperHero


@admin.register(Post)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin class for Post model.
    """

    list_display = ("hero", "content", "likes", "updated_at")
    list_per_page = settings.LIST_PER_PAGE


@admin.register(SuperHero)
class SuperHeroAdmin(admin.ModelAdmin):
    """
    Admin class for SuperHero model
    """

    list_display = ("name", "power", "updated_at")
    list_per_page = settings.LIST_PER_PAGE
