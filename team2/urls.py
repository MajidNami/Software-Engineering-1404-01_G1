from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name="team2_base"),
    path("ping/", views.ping, name="team2_ping"),

    # Home pages
    path("student/home/", views.student_home, name="team2_student_home"),
    path("teacher/home/", views.teacher_home, name="team2_teacher_home"),

    # Student URLs
    path("lessons/", views.lessons_list_view, name="team2_lessons_list"),
    path("lessons/rating/", views.lessons_with_rating_view, name="team2_lessons_rating"),
    path("lessons/<int:lesson_id>/", views.lesson_details_view, name="team2_lesson_details"),
    
    path("browse/", views.browse_lessons_view, name="browse_lessons"),
    path("browse/<int:lesson_id>/enroll/", views.enroll_lesson_view, name="enroll_lesson"),
    path("student/lessons/<int:lesson_id>/videos/", views.student_lesson_videos_view, name="student_lesson_videos"),
    path("student/lessons/<int:lesson_id>/watch/<int:video_id>/", views.watch_video_view, name="watch_video"),
    
    path("teacher/lessons/", views.teacher_lessons_view, name="team2_teacher_lessons"),
    path("teacher/lessons/create/", views.teacher_create_lesson_view, name="teacher_create_lesson"),
    path("teacher/lessons/<int:lesson_id>/publish/", views.publish_lesson_view, name="publish_lesson"),
    path("teacher/lessons/<int:lesson_id>/videos/", views.teacher_lesson_videos_view, name="teacher_lesson_videos"),
    path("teacher/lessons/<int:lesson_id>/add-video/", views.add_video_view, name="teacher_add_video"),
    path("teacher/dashboard/", views.teacher_dashboard_view, name="teacher_dashboard"),

    # Admin URLs
    path("admin/users/", views.admin_users_view, name="admin_users"),
    path("admin/users/<int:user_id>/change-role/", views.admin_change_role_view, name="admin_change_role"),

    # Rating API URLs
    path("api/lessons/<int:lesson_id>/rate/", views.rate_lesson_api, name="rate_lesson_api"),
    path("api/lessons/<int:lesson_id>/ratings/", views.lesson_ratings_api, name="lesson_ratings_api"),

    # Q&A API URLs
    path("api/lessons/<int:lesson_id>/ask/", views.ask_question_api, name="ask_question_api"),
    path("api/questions/<int:question_id>/answer/", views.answer_question_api, name="answer_question_api"),
    path("api/lessons/<int:lesson_id>/questions/", views.lesson_questions_api, name="lesson_questions_api"),

    # Statistics & Analytics API URLs
    path("api/lessons/<int:lesson_id>/track-view/", views.track_view_api, name="track_view_api"),
    path("api/teacher/lessons/<int:lesson_id>/stats/", views.teacher_lesson_stats_api, name="teacher_lesson_stats_api"),
]