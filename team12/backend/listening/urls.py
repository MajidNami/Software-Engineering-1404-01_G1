from django.urls import path
from . import views

urlpatterns = [
    path('tests/', views.TestsListView.as_view()),
    path('sessions/start/', views.SessionStartView.as_view()),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view()),
    path('sessions/<int:pk>/finish/', views.SessionFinishView.as_view()),
    path('sessions/<int:pk>/answers/', views.SessionAnswersView.as_view()),
    path('sessions/<int:pk>/events/', views.SessionEventsView.as_view()),
    path('sessions/<int:pk>/score-report/', views.SessionScoreReportView.as_view()),
    path('items/<int:item_id>/', views.ItemDetailView.as_view()),
]
