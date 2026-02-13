from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name="team15-home"),
    path("dashboard/", views.dashboard_page, name="team15-dashboard-page"),
    path("exam-setup/", views.exam_setup_page, name="team15-exam-setup-page"),
    path("exam-reading/", views.exam_reading_page, name="team15-exam-reading-page"),
    path("practice-reading/", views.practice_reading_page, name="team15-practice-reading-page"),
    path("exam-result/", views.exam_result_page, name="team15-exam-result-page"),
    path("review/", views.exam_review_page, name="team15-exam-review-page"),
    path("progress/", views.progress_tracking_page, name="team15-progress-page"),
    path("ping/", views.ping),

    # API endpoints
    path("api/tests/", views.test_list, name="team15-test-list"),
    path("api/tests/<int:test_id>/", views.test_detail, name="team15-test-detail"),
    path("api/attempts/start/", views.start_attempt, name="team15-start-attempt"),
    path("api/attempts/answer/", views.submit_answer_practice, name="team15-submit-answer"),
    path("api/attempts/submit/", views.submit_exam, name="team15-submit-exam"),
    path("api/attempts/finish/", views.finish_practice, name="team15-finish-practice"),
    path("api/attempts/<int:attempt_id>/result/", views.attempt_result, name="team15-attempt-result"),
    path("api/history/", views.user_history, name="team15-user-history"),
    path("api/dashboard/", views.user_dashboard, name="team15-user-dashboard"),
]
