from django.urls import path
from . import views
from .views import analysis_views

urlpatterns = [
    path("", views.base),
    path("ping/", views.ping),
    path('analysis/', analysis_views.text_analysis_page, name='analysis_page'),
    path('api/reading-history/', analysis_views.api_get_history, name='api_history'),
    path('api/text-analysis/', analysis_views.api_run_analysis, name='api_run_analysis'),
]