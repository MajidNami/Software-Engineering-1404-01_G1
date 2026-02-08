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
    
    # Health Check (FR-API-01)
    path("ping/", views.ping, name="ping"),
    
    # HTML Views (Front-end)
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
]