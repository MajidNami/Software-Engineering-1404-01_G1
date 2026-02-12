from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Creating a router for the REST API ViewSets
router = DefaultRouter()
router.register(r'lessons', views.LessonViewSet)
router.register(r'words', views.WordViewSet)

urlpatterns = [
    # Standard team app endpoints (required by repo pattern)
    path("", views.base, name="base"),
    path("ping/", views.ping, name="ping"),
    
    # Dashboard endpoint
    path("api/dashboard/", views.dashboard_stats, name="dashboard_stats"),
    
    # Vocabulary API endpoints
    path("api/", include(router.urls)),
]
