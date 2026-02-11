from django.urls import path
from . import views

urlpatterns = [
    path("", views.base),
    path("ping/", views.ping),
    path("exams/", views.exam),
    path("test/", views.test),
]