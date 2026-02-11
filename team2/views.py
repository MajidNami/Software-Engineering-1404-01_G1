from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods

from core.auth import api_login_required
from team2.models import Lesson

TEAM_NAME = "team2"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


@require_http_methods(["GET"])
def lessons_list_view(request):

    lessons = Lesson.objects.filter(
        # TODO : add filter user
        is_deleted=False,
        status='published'
    ).prefetch_related('videos')

    context = {
        'lessons': lessons,
        'total_lessons': lessons.count(),
    }
    # TODO : create team2_Lessons_list.html
    return render(request, 'team2_Lessons_list.html', context)


@require_http_methods(["GET"])
def lesson_details_view(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id,
        is_deleted=False,
        status='published'
    )

    videos = lesson.videos.filter(is_deleted=False).order_by('-uploaded_at')

    context = {
        'lesson': lesson,
        'videos': videos,
        'total_videos': videos.count(),
    }
    # TODO : create team2_lesson_details.html
    return render(request, 'team2_lesson_details.html', context)