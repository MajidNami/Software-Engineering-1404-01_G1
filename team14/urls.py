from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name='base'),
    path("ping/", views.ping, name='ping'),
    path('reading/training-levels/', views.training_levels, name='training_levels'),
    path('easy/', views.easy_level, name='easy_level'),
    path('medium/', views.mid_level, name='mid_level'),
    path('hard/', views.hard_level, name='hard_level'),
    path('exam/', views.Exam_Page, name='Exam_Page'),
    path('practice/<int:passage_id>/', views.practice_page, name='practice_page'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),

    # ✅ دو مسیر جداگانه برای finish
    path('practice/finish/<int:session_id>/', views.finish_practice, name='finish_practice'),
    path('exam/finish/<int:session_id>/', views.finish_exam, name='finish_exam'),

    # ✅ دو مسیر جداگانه برای result
    path('practice/result/<int:session_id>/', views.practice_result, name='practice_result'),
    path('exam/result/<int:session_id>/', views.exam_result, name='exam_result'),

    path('exam/start/', views.start_exam, name='start_exam'),
    path('about/', views.about, name='about'),
    path('start_learning/', views.start_learning, name='start_learning'),
]
