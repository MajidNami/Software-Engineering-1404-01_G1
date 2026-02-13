from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'team7'

team_patterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('exams/', views.exams, name='exams'),
    path('writing-exam/', views.writing_exam, name='writing_exam'),
    path('speaking-exam/', views.speaking_exam, name='speaking_exam'),
    path('api/submit-writing/', views.submit_writing, name='submit_writing'),
    path('api/submit-speaking/', views.submit_speaking, name='submit_speaking'),
    path('api/submit-speaking-mock/', views.submit_speaking_mock, name='submit_speaking_mock'),
    path('api/history/', views.get_history, name='get_history'),
    path('api/v1/history/<str:user_id>/', views.get_history, name='get_history_v1'),
    path('api/analytics/', views.get_analytics, name='get_analytics'),
    path('api/ping/', views.ping, name='ping'),
    path('api/health/', views.admin_health, name='admin_health'),
    path('api/exams/', views.list_exams, name='list_exams'),
    path('favicon.ico', views.favicon, name='favicon'),
]

urlpatterns = team_patterns