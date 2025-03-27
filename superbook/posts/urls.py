from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path("adds", views.PostCreateView.as_view(), name="adds"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="detail"),
]
