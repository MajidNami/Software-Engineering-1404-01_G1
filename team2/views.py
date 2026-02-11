from django.http import JsonResponse
from django.shortcuts import render
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