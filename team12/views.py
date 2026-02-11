import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from core.auth import api_login_required
from .models import (
    ListeningEventLog,
    ListeningPracticeAnswer,
    ListeningPracticeSession,
)

TEAM_NAME = "team12"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

def listening_practice(request):
    user_id = (
        request.user.id
        if getattr(request, "user", None) and request.user.is_authenticated
        else None
    )
    active_session = None
    if user_id is not None:
        active_session = ListeningPracticeSession.objects.filter(
            user_id=user_id, status=ListeningPracticeSession.Status.ACTIVE
        ).order_by("-started_at").first()
    context = {
        "has_active_session": active_session is not None,
        "session_id": active_session.id if active_session else "",
    }
    return render(request, f"{TEAM_NAME}/listening_practice.html", context)


def _parse_json(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


def _get_session_or_404(session_id):
    try:
        return ListeningPracticeSession.objects.get(id=session_id)
    except ListeningPracticeSession.DoesNotExist:
        return None


@csrf_exempt
#@api_login_required
def listening_practice_start(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    session = ListeningPracticeSession.objects.using("team12").create(
        user_id=getattr(request.user, "id", None)
    )
    return JsonResponse({"session_id": session.id})


@csrf_exempt

#@api_login_required
@require_http_methods(["POST"])
def listening_practice_answer(request):
    payload = _parse_json(request)
    if payload is None:
        return JsonResponse({"error": "invalid json"}, status=400)

    session = _get_session_or_404(payload.get("session_id"))
    if not session:
        return JsonResponse({"error": "session not found"}, status=404)

    ListeningPracticeAnswer.objects.create(
        session=session,
        question_number=payload.get("question_number"),
        selected_choice=payload.get("selected_choice", ""),
        is_correct=bool(payload.get("is_correct", False)),
        time_spent_seconds=payload.get("time_spent_seconds"),
    )
    return JsonResponse({"ok": True})

@csrf_exempt

#@api_login_required
@require_http_methods(["POST"])
def listening_practice_event(request):
    payload = _parse_json(request)
    if payload is None:
        return JsonResponse({"error": "invalid json"}, status=400)

    session = _get_session_or_404(payload.get("session_id"))
    if not session:
        return JsonResponse({"error": "session not found"}, status=404)

    event_type = payload.get("event_type")
    if event_type not in ListeningEventLog.EventType.values:
        return JsonResponse({"error": "invalid event_type"}, status=400)

    ListeningEventLog.objects.create(
        session=session,
        event_type=event_type,
        meta=payload.get("meta"),
    )
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def listening_practice_result(request, session_id):
    session = _get_session_or_404(session_id)
    if not session:
        return JsonResponse({"error": "session not found"}, status=404)

    if session.status != ListeningPracticeSession.Status.FINISHED:
        session.status = ListeningPracticeSession.Status.FINISHED
        session.finished_at = timezone.now()
        session.save(update_fields=["status", "finished_at"])

    answers = list(session.answers.order_by("question_number"))
    score = sum(1 for answer in answers if answer.is_correct)
    context = {
        "session": session,
        "answers": answers,
        "score": score,
    }
    return render(request, f"{TEAM_NAME}/listening_result.html", context)
