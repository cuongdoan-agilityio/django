from django.contrib.admin.apps import AdminConfig


class CustomAdminConfig(AdminConfig):
    """
    A custom configuration for the Django admin application.
    """

    default_site = "config.admin.CustomAdminSite"
