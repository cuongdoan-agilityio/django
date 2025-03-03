from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.contrib.admindocs import urls as admindocs_urls
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin-dashboard/doc/", include(admindocs_urls)),
    path("admin-dashboard/", admin.site.urls),
    path("docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

# API URLS
urlpatterns += [
    path(settings.API_ROOT_ENDPOINT, include("config.api_router")),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
