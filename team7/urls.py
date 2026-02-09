from django.urls import path
from . import views

app_name = 'team7'

urlpatterns = [
    # API Endpoints (Controller Layer - SDD Section 2.A)
    
    # Writing Evaluation Endpoint (UC-01, FR-WR, FR-API-02)
    path("api/v1/evaluate/writing/", views.submit_writing, name="evaluate-writing"),
    
    # Speaking Evaluation Endpoint (UC-02, FR-SP, FR-API-02)
    path("api/v1/evaluate/speaking/", views.submit_speaking, name="evaluate-speaking"),
    
    # Student History/Progress Endpoint (UC-03, FR-MON)
    path("api/v1/history/", views.get_history, name="get-history"),
    path("api/v1/history/<str:user_id>/", views.get_history, name="get-history-by-user"),
    
    # Analytics Endpoint with Trends (UC-03, FR-MON-02)
    path("api/v1/analytics/", views.get_analytics, name="get-analytics"),
    path("api/v1/analytics/<str:user_id>/", views.get_analytics, name="get-analytics-by-user"),
    
    # Admin Health Monitoring (UC-04, FR-MON, NFR-AVAIL-01)
    path("api/v1/admin/health/", views.admin_health, name="admin-health"),
    
    # Health Check (FR-API-01)
    path("ping/", views.ping, name="ping"),
    
    # HTML Views (Front-end)
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("exams/", views.exams, name="exams"),
    path("writing-exam/", views.writing_exam, name="writing-exam"),
    path("speaking-exam/", views.speaking_exam, name="speaking-exam"),
]