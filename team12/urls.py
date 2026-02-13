from django.urls import path
from . import views

urlpatterns = [
    path("", views.base),
    path("ping/", views.ping),
    path("listening/practice/", views.listening_practice),
    path("listening/practice/start/", views.listening_practice_start),
    path("listening/practice/answer/", views.listening_practice_answer),
    path("listening/practice/event/", views.listening_practice_event),
    path(
        "listening/practice/result/<int:session_id>/",
        views.listening_practice_result,
    ),
]
