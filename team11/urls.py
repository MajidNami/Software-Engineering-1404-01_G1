from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name="team11_home"),
    path("ping/", views.ping, name="team11_ping"),
    path("dashboard/", views.dashboard, name="team11_dashboard"),
    path("start-exam/", views.start_exam, name="team11_start_exam"),
    path("writing-exam/", views.writing_exam, name="team11_writing_exam"),
    path("speaking-exam/", views.speaking_exam, name="team11_speaking_exam"),
    path("api/submit-writing/", views.submit_writing, name="team11_submit_writing"),
    path("api/submit-speaking/", views.submit_speaking, name="team11_submit_speaking"),
    path("api/submission-status/<uuid:submission_id>/", views.submission_status, name="team11_submission_status"),
    path("submission/<uuid:submission_id>/", views.submission_detail, name="team11_submission_detail"),
]