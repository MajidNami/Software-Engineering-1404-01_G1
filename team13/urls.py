from django.urls import path

from team13 import views


urlpatterns = [
    path("", views.base),
    path("ping/", views.ping),
    path("get_question/", views.get_question),
    path("submit_response/", views.submit_response),
    path("get_user_report/", views.get_user_report)
]
