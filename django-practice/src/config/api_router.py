import contextlib
from importlib import import_module

from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter


api_routers = DefaultRouter() if settings.DEBUG else SimpleRouter()

# Load all api apps from settings.
for local_app in settings.LOCAL_APPS:
    api_module = import_module(f"{local_app}.api.views", "apps")

    with contextlib.suppress(Exception):
        # Try to register API views
        print("api_module.apps:", api_module.apps)
        for viewset in api_module.apps:
            api_routers.register(
                viewset.resource_name,
                viewset,
                viewset.resource_name,
            )


app_name = "api"
urlpatterns = []
urlpatterns += api_routers.urls
