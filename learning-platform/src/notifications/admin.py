from django.contrib import admin
from django.conf import settings
from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Notification model.
    """

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    list_display = ("id", "user", "message", "is_read", "modified")
    list_per_page = settings.ADMIN_PAGE_SIZE
    list_filter = ["is_read", "user"]
    search_fields = ["message"]
    ordering = ["-modified"]
