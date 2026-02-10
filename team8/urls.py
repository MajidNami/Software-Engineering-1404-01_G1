from django.urls import path
from . import views # This now refers to the views/ folder

urlpatterns = [
    # Original paths
    path("", views.base),
    path("ping/", views.ping),
    
    # New WordCard path
    path("wordcard/", views.WordCardView.as_view(), name="wordcard"),
]