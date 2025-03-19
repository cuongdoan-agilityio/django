from django.contrib.admin import AdminSite


class CustomAdminSite(AdminSite):
    """
    A custom implementation of the Django AdminSite.
    """

    def get_app_list(self, request):
        """
        Returns a filtered list of apps to display in the admin interface.
        """

        app_list = super().get_app_list(request)
        return [
            app for app in app_list if app["app_label"] not in ["authtoken", "auth"]
        ]
