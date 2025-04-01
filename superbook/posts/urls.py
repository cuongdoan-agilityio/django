from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("list", views.PostListView.as_view(), name="index"),
    path("adds", views.PostCreateView.as_view(), name="adds"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="detail"),
    path("", views.PostView.as_view(), name="post-list"),
]
