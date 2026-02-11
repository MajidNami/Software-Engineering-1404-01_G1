from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name="team11_home"),
    path("ping/", views.ping, name="team11_ping"),
    path("dashboard/", views.dashboard, name="team11_dashboard"),
    path("start-exam/", views.start_exam, name="team11_start_exam"),
    path("writing-exam/", views.writing_exam, name="team11_writing_exam"),
    path("listening-exam/", views.listening_exam, name="team11_listening_exam"),
    path("api/submit-writing/", views.submit_writing, name="team11_submit_writing"),
    path("api/submit-listening/", views.submit_listening, name="team11_submit_listening"),
    path("api/submission-status/<uuid:submission_id>/", views.submission_status, name="team11_submission_status"),
    path("submission/<uuid:submission_id>/", views.submission_detail, name="team11_submission_detail"),
]