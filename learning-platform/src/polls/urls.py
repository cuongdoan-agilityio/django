from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    # ex: /polls/
    path("", views.IndexView.as_view(), name="index"),
    # ex: /polls/5/
    path("<uuid:pk>/", views.DetailPollView.as_view(), name="detail"),
    # ex: /polls/5/results/
    path("<uuid:pk>/results/", views.ResultsView.as_view(), name="results"),
    # ex: polls/questions/5/vote/
    path("questions/<uuid:question_id>/vote/", views.vote, name="question-vote"),
]
