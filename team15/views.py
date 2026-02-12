from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from functools import wraps
from collections import defaultdict
from datetime import timedelta
import calendar
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from core.jwt_utils import decode_token

from .models import Test, Question, TestAttempt, Answer
from .serializers import (
    TestListSerializer, TestDetailSerializer,
    StartAttemptSerializer, SubmitAnswerSerializer,
    SubmitExamSerializer, FinishPracticeSerializer,
    AttemptResultSerializer, AttemptHistorySerializer,
)
from .scoring import calculate_score, calculate_accuracy

TEAM_NAME = "team15"
User = get_user_model()


def _request_user(request):
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return user

    raw_request = getattr(request, "_request", None)
    raw_user = getattr(raw_request, "user", None)
    if raw_user is not None and getattr(raw_user, "is_authenticated", False):
        return raw_user

    cookies = getattr(request, "COOKIES", None) or getattr(raw_request, "COOKIES", {}) or {}
    access_token = cookies.get("access_token")
    if not access_token:
        return None

    try:
        payload = decode_token(access_token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        tv = payload.get("tv")
        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            return None
        if user.token_version != tv:
            return None
        return user
    except Exception:
        return None
    return None


def _get_user_id(request, data=None):
    user = _request_user(request)
    if user is not None and hasattr(user, "id"):
        return str(user.id)
    if data and data.get("user_id"):
        return data["user_id"]
    query_params = getattr(request, "query_params", None)
    if query_params is not None:
        return query_params.get("user_id")
    return request.GET.get("user_id")


def _page_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return redirect(f"/auth/?next={request.get_full_path()}")
        return view_func(request, *args, **kwargs)
    return _wrapped


def _api_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if _request_user(request) is None:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        return view_func(request, *args, **kwargs)
    return _wrapped


def _format_mmss(seconds):
    if seconds is None:
        return "00:00"
    total = max(int(seconds), 0)
    minutes, sec = divmod(total, 60)
    return f"{minutes:02d}:{sec:02d}"


def _format_time_compact(seconds):
    if seconds is None:
        return "0s"
    total = max(int(seconds), 0)
    minutes, sec = divmod(total, 60)
    if minutes:
        return f"{minutes}m {sec}s"
    return f"{sec}s"


def _relative_date(dt):
    if not dt:
        return "-"
    delta_days = (timezone.now().date() - dt.date()).days
    if delta_days <= 0:
        return "Today"
    if delta_days == 1:
        return "Yesterday"
    return f"{delta_days} days ago"


def _score_to_30(score):
    if score is None:
        return 0
    return max(0, min(30, int(round(score))))


def _pct_from_score_30(score):
    base = _score_to_30(score)
    return int(round((base / 30) * 100))


def _choice_list(choices, size=4):
    values = list(choices or [])
    if len(values) < size:
        values.extend([""] * (size - len(values)))
    return values[:size]


def _safe_percentage(value, total):
    if not total:
        return 0
    return int(round((value / total) * 100))


def _question_type_label(qtype):
    mapping = {
        "multiple_choice": "Multiple Choice",
        "insert_text": "Insert Sentence",
        "inference": "Inference",
        "vocabulary": "Vocabulary",
        "main_idea": "Main Idea",
        "detail": "Detail",
        "purpose": "Purpose",
    }
    return mapping.get(qtype, str(qtype).replace("_", " ").title() if qtype else "Question")


def _month_start(dt):
    local_dt = timezone.localtime(dt)
    return local_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _add_months(dt, months):
    month_index = dt.month - 1 + months
    year = dt.year + (month_index // 12)
    month = (month_index % 12) + 1
    return dt.replace(year=year, month=month, day=1)


def _shift_months_preserving_day(dt, months):
    local_dt = timezone.localtime(dt)
    month_index = local_dt.month - 1 + months
    year = local_dt.year + (month_index // 12)
    month = (month_index % 12) + 1
    day = min(local_dt.day, calendar.monthrange(year, month)[1])
    return local_dt.replace(year=year, month=month, day=day)


def _percent_change(current, previous):
    current_value = float(current or 0)
    previous_value = float(previous or 0)
    if previous_value == 0:
        return 100.0 if current_value > 0 else 0.0
    return ((current_value - previous_value) / abs(previous_value)) * 100.0


def _signed_percent(value):
    amount = float(value or 0)
    sign = "+" if amount > 0 else ""
    return f"{sign}{amount:.1f}%"


def _signed_seconds(value):
    amount = int(round(float(value or 0)))
    sign = "+" if amount > 0 else ""
    return f"{sign}{amount}s"


def _signed_int(value):
    amount = int(round(float(value or 0)))
    sign = "+" if amount > 0 else ""
    return f"{sign}{amount}"


def _build_trend_paths(values):
    points = list(values or [])
    if not points:
        points = [0, 0, 0, 0]

    width = 472.0
    height = 149.0
    chart_height = 148.0

    if len(points) == 1:
        x_positions = [0.0]
    else:
        step = width / (len(points) - 1)
        x_positions = [idx * step for idx in range(len(points))]

    line_points = []
    for x, raw_value in zip(x_positions, points):
        bounded = max(0.0, min(float(raw_value), 100.0))
        y = height - ((bounded / 100.0) * chart_height)
        line_points.append((round(x, 2), round(y, 2)))

    line_path = "M " + " L ".join(f"{x} {y}" for x, y in line_points)
    first_x = line_points[0][0]
    area_path = f"{line_path} V {height} H {first_x} Z"
    return area_path, line_path


def _dashboard_context(user):
    user_id = str(user.id)
    attempts_qs = TestAttempt.objects.filter(user_id=user_id).select_related("test").order_by("-started_at")
    completed_qs = attempts_qs.filter(status="completed")
    answers_qs = Answer.objects.filter(attempt__user_id=user_id).select_related("question")

    avg_score = completed_qs.aggregate(v=Avg("score"))["v"]
    avg_time_q = answers_qs.filter(time_spent__gt=0).aggregate(v=Avg("time_spent"))["v"]
    if not avg_time_q:
        total_answered = answers_qs.count()
        total_attempt_time = sum(int(item.total_time or 0) for item in completed_qs if item.total_time)
        if total_answered > 0 and total_attempt_time > 0:
            avg_time_q = total_attempt_time / total_answered

    recent_attempts = []
    for attempt in completed_qs[:3]:
        pct = _pct_from_score_30(attempt.score)
        color = "text-state-success"
        if pct < 70:
            color = "text-state-warning"
        if pct < 50:
            color = "text-state-error"
        recent_attempts.append({
            "type_label": f"{'Full Exam' if attempt.test.mode == 'exam' else 'Practice'}: {attempt.test.title}",
            "score_label": f"{_score_to_30(attempt.score)}/30",
            "score_class": color,
            "date_label": _relative_date(attempt.started_at),
            "review_url": f"/team15/exam-result/?attempt_id={attempt.id}",
        })

    recent_scores = []
    recent_items = list(completed_qs.exclude(score__isnull=True)[:5])[::-1]
    recent_pcts = [_pct_from_score_30(item.score) for item in recent_items]
    max_pct = max(recent_pcts) if recent_pcts else 0
    for item in recent_items:
        pct = _pct_from_score_30(item.score)
        normalized_height = int(round((pct / max_pct) * 100)) if max_pct > 0 else 0
        if pct >= 70:
            bar_class = "bg-state-success"
        elif pct >= 50:
            bar_class = "bg-state-warning"
        else:
            bar_class = "bg-state-error"
        recent_scores.append({
            "height": max(12, normalized_height) if pct > 0 else 8,
            "label": timezone.localtime(item.started_at).strftime("%m/%d"),
            "value_label": f"{_score_to_30(item.score)}/30",
            "bar_class": bar_class,
        })
    while len(recent_scores) < 5:
        recent_scores.append({
            "height": 0,
            "label": "",
            "value_label": "",
            "bar_class": "bg-primary-600/20",
        })

    by_type = defaultdict(lambda: {"correct": 0, "total": 0})
    for answer in answers_qs:
        qtype = answer.question.question_type if answer.question_id else "multiple_choice"
        by_type[qtype]["total"] += 1
        if answer.is_correct:
            by_type[qtype]["correct"] += 1

    weakest_type = None
    weakest_accuracy = None
    for qtype, item in by_type.items():
        total = item["total"] or 1
        accuracy = int(round((item["correct"] / total) * 100))
        if weakest_accuracy is None or accuracy < weakest_accuracy:
            weakest_accuracy = accuracy
            weakest_type = qtype

    display_name = user.first_name or getattr(user, "username", "") or "User"

    return {
        "user_display_name": display_name,
        "proficiency_pct": _pct_from_score_30(avg_score),
        "proficiency_dashoffset": max(0, 100 - _pct_from_score_30(avg_score)),
        "average_score_pct": _pct_from_score_30(avg_score),
        "avg_time_per_question": _format_time_compact(avg_time_q),
        "questions_answered": answers_qs.count(),
        "recent_attempts": recent_attempts,
        "recent_scores": recent_scores[:5],
        "weak_skill_name": _question_type_label(weakest_type) if weakest_type else "Reading",
        "weak_skill_accuracy": weakest_accuracy if weakest_accuracy is not None else 0,
    }


def _exam_setup_context():
    tests = list(
        Test.objects.filter(is_active=True, mode="exam")
        .annotate(passage_count=Count("passages"), question_count=Count("passages__questions"))
        .order_by("id")
    )
    session_options = []
    for idx, test in enumerate(tests[:2]):
        session_options.append({
            "label": f"{test.passage_count} Passages",
            "value": str(test.id),
            "test_id": test.id,
            "time_limit": test.time_limit or 0,
            "selected": idx == 0,
        })
    while len(session_options) < 2:
        session_options.append({
            "label": "0 Passages",
            "value": "",
            "test_id": "",
            "time_limit": 0,
            "selected": False,
        })
    selected = session_options[0] if session_options else {"time_limit": 0, "test_id": ""}
    return {
        "passage_option_1": session_options[0]["label"],
        "passage_option_2": session_options[1]["label"],
        "estimated_minutes": selected["time_limit"],
        "default_test_id": selected["test_id"],
        "session_options": session_options,
    }


def _exam_reading_context(user, request):
    selected_test_id = request.GET.get("test_id")
    selected_attempt_id = request.GET.get("attempt_id")
    tests_qs = Test.objects.filter(is_active=True, mode="exam").prefetch_related("passages__questions").order_by("id")
    if selected_test_id:
        test = tests_qs.filter(id=selected_test_id).first()
    else:
        test = tests_qs.first()
    if not test:
        return {
            "timer_hours": "00",
            "timer_minutes": "00",
            "timer_seconds": "00",
            "exam_remaining_seconds": 0,
            "exam_time_limited": False,
            "passage_title": "",
            "paragraph_1": "",
            "paragraph_2": "",
            "paragraph_3": "",
            "question_number": 0,
            "total_questions": 0,
            "question_text": "",
            "choice_1": "",
            "choice_2": "",
            "choice_3": "",
            "choice_4": "",
            "paragraphs": [],
            "question_choices": [],
            "question_map": [],
            "question_progress_pct": 0,
            "exam_test_id": "",
            "exam_attempt_id": "",
            "exam_question_id": "",
            "exam_answered_count": 0,
            "exam_is_first": True,
            "exam_is_last": True,
            "exam_prev_q": 1,
            "exam_next_q": 1,
        }

    user_id = str(user.id)
    if selected_attempt_id:
        attempt = TestAttempt.objects.filter(
            id=selected_attempt_id,
            user_id=user_id,
            test=test,
            status="in_progress",
        ).first()
    else:
        attempt = None

    if attempt is None:
        attempt = (
            TestAttempt.objects.filter(user_id=user_id, test=test, status="in_progress")
            .order_by("-started_at")
            .first()
        )

    if attempt is None:
        attempt = TestAttempt.objects.create(user_id=user_id, test=test)

    attempt_id = attempt.id if attempt else ""

    questions = list(
        Question.objects.filter(passage__test=test)
        .select_related("passage")
        .order_by("passage__order", "order", "id")
    )
    total_questions = len(questions)
    q_param = request.GET.get("q", "1")
    try:
        question_number = int(q_param)
    except (TypeError, ValueError):
        question_number = 1
    question_number = max(1, min(question_number, max(total_questions, 1)))
    question = questions[question_number - 1] if questions else None
    passage = question.passage if question else None

    time_limit_seconds = max(int((test.time_limit or 0) * 60), 0)
    if time_limit_seconds > 0 and attempt and attempt.started_at:
        elapsed_seconds = int((timezone.now() - attempt.started_at).total_seconds())
        remaining_seconds = max(time_limit_seconds - elapsed_seconds, 0)
    else:
        remaining_seconds = time_limit_seconds

    hours, rem = divmod(remaining_seconds, 3600)
    mins, sec = divmod(rem, 60)

    paragraphs = [p.strip() for p in (passage.content.splitlines() if passage else []) if p.strip()]
    while len(paragraphs) < 3:
        paragraphs.append("")

    choices = _choice_list(question.choices if question else [])
    question_number = question_number if question else 0
    question_progress_pct = _safe_percentage(question_number, total_questions)

    answered_question_ids = set()
    if attempt:
        answered_question_ids = set(
            Answer.objects.filter(attempt=attempt).values_list("question_id", flat=True)
        )

    question_map = []
    for idx, q_item in enumerate(questions, start=1):
        state = "pending"
        if idx == question_number:
            state = "current"
        elif q_item.id in answered_question_ids:
            state = "answered"
        question_map.append({
            "number": idx,
            "state": state,
            "question_id": q_item.id,
        })

    return {
        "timer_hours": f"{hours:02d}",
        "timer_minutes": f"{mins:02d}",
        "timer_seconds": f"{sec:02d}",
        "exam_remaining_seconds": remaining_seconds,
        "exam_time_limited": time_limit_seconds > 0,
        "passage_title": passage.title if passage else "",
        "paragraph_1": paragraphs[0],
        "paragraph_2": paragraphs[1],
        "paragraph_3": paragraphs[2],
        "question_number": question_number,
        "total_questions": total_questions,
        "question_text": question.question_text if question else "",
        "choice_1": choices[0],
        "choice_2": choices[1],
        "choice_3": choices[2],
        "choice_4": choices[3],
        "paragraphs": paragraphs[:3],
        "question_choices": choices,
        "question_map": question_map,
        "question_progress_pct": question_progress_pct,
        "exam_test_id": test.id if test else "",
        "exam_attempt_id": attempt_id,
        "exam_question_id": question.id if question else "",
        "exam_answered_count": len(answered_question_ids),
        "exam_is_first": question_number <= 1,
        "exam_is_last": question_number >= total_questions if total_questions else True,
        "exam_prev_q": max(1, question_number - 1),
        "exam_next_q": min(total_questions if total_questions else 1, question_number + 1),
    }


def _practice_context(user, request):
    user_id = str(user.id)
    selected_test_id = request.GET.get("test_id")
    selected_attempt_id = request.GET.get("attempt_id")

    tests_qs = Test.objects.filter(is_active=True, mode="practice").order_by("id")
    if selected_test_id:
        test = tests_qs.filter(id=selected_test_id).first()
    else:
        test = tests_qs.first()

    if not test:
        return {
            "practice_question_index": 1,
            "practice_total_questions": 0,
            "practice_progress_pct": 0,
            "practice_passage_title": "",
            "practice_question_text": "",
            "practice_explanation": "Answer explanation will appear after submission.",
            "practice_skill_focus": "Reading",
            "practice_paragraphs": [],
            "practice_choice_rows": [],
            "practice_result_title": "",
            "practice_has_answer": False,
            "practice_selected_answer": "",
            "practice_correct_answer": "",
            "practice_is_correct": False,
            "practice_test_id": "",
            "practice_attempt_id": "",
            "practice_question_id": "",
            "practice_prev_url": "#",
            "practice_next_url": "#",
            "practice_is_first": True,
            "practice_is_last": True,
        }

    if selected_attempt_id:
        attempt = TestAttempt.objects.filter(
            id=selected_attempt_id,
            user_id=user_id,
            test=test,
        ).first()
    else:
        attempt = None

    if attempt is None:
        attempt = (
            TestAttempt.objects.filter(user_id=user_id, test=test, status="in_progress")
            .order_by("-started_at")
            .first()
        )

    if attempt is None:
        attempt = TestAttempt.objects.create(user_id=user_id, test=test)

    questions = list(
        Question.objects.filter(passage__test=test)
        .select_related("passage")
        .order_by("passage__order", "order", "id")
    )
    total_questions = len(questions)
    q_param = request.GET.get("q", "1")
    try:
        question_index = int(q_param)
    except (TypeError, ValueError):
        question_index = 1
    question_index = max(1, min(question_index, max(total_questions, 1)))
    question = questions[question_index - 1] if questions else None
    passage = question.passage if question else None
    current_answer = (
        Answer.objects.filter(attempt=attempt, question=question).select_related("question").first()
        if question else None
    )

    paragraphs = [p.strip() for p in (passage.content.splitlines() if passage else []) if p.strip()]
    choices = _choice_list(question.choices if question else [])

    selected = current_answer.selected_answer if current_answer else ""
    correct = question.correct_answer if question else ""
    has_answer = current_answer is not None

    progress_pct = int(round((question_index / total_questions) * 100)) if total_questions else 0

    choice_rows = []
    for idx, choice_text in enumerate(choices, start=1):
        option_id = f"option{idx}"
        is_selected = bool(selected and selected == choice_text)
        is_correct_choice = bool(correct and correct == choice_text)
        status = "default"
        if has_answer:
            if is_correct_choice:
                status = "correct"
            if is_selected and not is_correct_choice:
                status = "incorrect"
        choice_rows.append({
            "id": option_id,
            "text": choice_text,
            "is_selected": is_selected,
            "is_correct_choice": is_correct_choice,
            "status": status,
        })

    return {
        "practice_question_index": question_index,
        "practice_total_questions": total_questions,
        "practice_progress_pct": progress_pct,
        "practice_passage_title": passage.title if passage else "",
        "practice_paragraph_1": paragraphs[0] if len(paragraphs) > 0 else "",
        "practice_paragraph_2": paragraphs[1] if len(paragraphs) > 1 else "",
        "practice_paragraph_3": paragraphs[2] if len(paragraphs) > 2 else "",
        "practice_paragraph_4": paragraphs[3] if len(paragraphs) > 3 else "",
        "practice_question_text": question.question_text if question else "",
        "practice_choice_1": choices[0],
        "practice_choice_2": choices[1],
        "practice_choice_3": choices[2],
        "practice_choice_4": choices[3],
        "practice_selected_answer": selected,
        "practice_correct_answer": correct if has_answer else "",
        "practice_is_correct": bool(current_answer.is_correct) if has_answer else False,
        "practice_explanation": (
            f"The correct answer is: {correct}"
            if has_answer and correct
            else "Select an answer to see the explanation."
        ),
        "practice_skill_focus": _question_type_label(question.question_type) if question else "Reading",
        "practice_paragraphs": paragraphs[:4],
        "practice_choice_rows": choice_rows,
        "practice_result_title": "Correct" if (has_answer and current_answer.is_correct) else ("Incorrect" if has_answer else ""),
        "practice_has_answer": has_answer,
        "practice_test_id": test.id if test else "",
        "practice_attempt_id": attempt.id if attempt else "",
        "practice_question_id": question.id if question else "",
        "practice_prev_url": f"/team15/practice-reading/?test_id={test.id}&attempt_id={attempt.id}&q={max(1, question_index - 1)}" if test and attempt else "#",
        "practice_next_url": f"/team15/practice-reading/?test_id={test.id}&attempt_id={attempt.id}&q={min(total_questions if total_questions else 1, question_index + 1)}" if test and attempt else "#",
        "practice_is_first": question_index <= 1,
        "practice_is_last": question_index >= total_questions if total_questions else True,
    }


def _exam_result_context(user, request):
    user_id = str(user.id)
    attempt_id = request.GET.get("attempt_id")
    attempts = TestAttempt.objects.filter(user_id=user_id, status="completed").select_related("test").order_by("-started_at")
    attempt = attempts.filter(id=attempt_id).first() if attempt_id else attempts.first()
    if not attempt:
        return {
            "result_test_title": "No completed exam yet",
            "result_scaled_score": "0 / 30",
            "result_accuracy": 0,
            "result_total_time": "00:00",
            "result_avg_time": "00:00",
            "result_skill_rows": [],
            "result_answer_rows": [],
        }

    answers = list(
        Answer.objects.filter(attempt=attempt)
        .select_related("question", "question__passage")
        .order_by("question__order")
    )
    correct = sum(1 for a in answers if a.is_correct)
    total = len(answers)
    accuracy_float = calculate_accuracy(correct, total)
    accuracy = max(0, min(100, int(round(accuracy_float))))
    total_time = attempt.total_time or 0
    answer_time_values = [int(a.time_spent) for a in answers if a.time_spent and a.time_spent > 0]
    if answer_time_values:
        avg_time = int(round(sum(answer_time_values) / len(answer_time_values)))
    else:
        avg_time = int(round(total_time / total)) if total else 0

    skill_map = defaultdict(lambda: {"correct": 0, "total": 0})
    for ans in answers:
        label = _question_type_label(ans.question.question_type if ans.question_id else "")
        skill_map[label]["total"] += 1
        if ans.is_correct:
            skill_map[label]["correct"] += 1

    result_skill_rows = []
    for label, item in skill_map.items():
        pct = int(round((item["correct"] / item["total"]) * 100)) if item["total"] else 0
        result_skill_rows.append({
            "label": label,
            "pct": pct,
            "bar_class": "bg-primary-500" if pct >= 70 else ("bg-accent-orange" if pct >= 50 else "bg-error"),
        })
    result_skill_rows.sort(key=lambda x: x["pct"], reverse=True)

    result_answer_rows = []
    for idx, ans in enumerate(answers, start=1):
        result_answer_rows.append({
            "index": idx,
            "question_type": _question_type_label(ans.question.question_type if ans.question_id else ""),
            "selected_answer": ans.selected_answer,
            "correct_answer": ans.question.correct_answer if ans.question_id else "",
            "time_spent": _format_mmss(ans.time_spent or 0),
            "is_correct": ans.is_correct,
            "review_url": f"/team15/review/?attempt_id={attempt.id}&question_id={ans.question_id}",
            "row_class": "bg-gray-50/50 dark:bg-gray-800/20" if idx % 2 == 0 else "",
        })

    return {
        "result_attempt_id": attempt.id,
        "result_test_title": attempt.test.title,
        "result_scaled_score": f"{_score_to_30(attempt.score)} / 30",
        "result_accuracy": accuracy,
        "result_total_time": _format_mmss(total_time),
        "result_avg_time": _format_mmss(avg_time),
        "result_skill_rows": result_skill_rows,
        "result_answer_rows": result_answer_rows,
        "result_accuracy_dasharray": "100",
        "result_accuracy_dashoffset": max(0, 100 - accuracy),
    }


def _progress_context(user, request):
    user_id = str(user.id)
    selected_range = request.GET.get("range", "30d")
    if selected_range not in ("30d", "6m", "all"):
        selected_range = "30d"

    now = timezone.now()
    attempts_all_qs = (
        TestAttempt.objects.filter(user_id=user_id, status="completed")
        .select_related("test")
        .order_by("-started_at")
    )

    def filter_attempts_in_window(qs, start_dt, end_dt):
        if start_dt is None:
            return qs
        return qs.filter(started_at__gte=start_dt, started_at__lt=end_dt)

    def build_metrics(attempts_qs):
        attempts_list = list(attempts_qs)
        attempt_ids = [item.id for item in attempts_list]
        answers_qs = Answer.objects.filter(attempt_id__in=attempt_ids).select_related("question")

        score_values = [_score_to_30(item.score) for item in attempts_list if item.score is not None]
        avg_score_raw = (sum(score_values) / len(score_values)) if score_values else 0

        answer_count = answers_qs.count()
        correct_count = answers_qs.filter(is_correct=True).count()
        accuracy_pct = int(round((correct_count / answer_count) * 100)) if answer_count else 0
        avg_time_q = answers_qs.filter(time_spent__gt=0).aggregate(v=Avg("time_spent"))["v"] or 0
        if not avg_time_q:
            total_attempt_time = sum(int(item.total_time or 0) for item in attempts_list if item.total_time)
            if answer_count > 0 and total_attempt_time > 0:
                avg_time_q = total_attempt_time / answer_count

        return {
            "attempts": attempts_list,
            "answers_qs": answers_qs,
            "avg_score_raw": avg_score_raw,
            "accuracy_pct": accuracy_pct,
            "avg_time_q": float(avg_time_q or 0),
            "sessions_count": len(attempts_list),
        }

    def delta_class(value, positive_good=True):
        amount = float(value or 0)
        if amount > 0:
            return "text-positive" if positive_good else "text-warning"
        if amount < 0:
            return "text-state-error" if positive_good else "text-positive"
        return "text-text-light dark:text-gray-400"

    compare_label = "vs previous 30 days"
    previous_start = None
    previous_end = None

    if selected_range == "30d":
        current_start = now - timedelta(days=30)
        current_end = now
        previous_start = current_start - timedelta(days=30)
        previous_end = current_start

        trend_labels = [f"Week {idx}" for idx in range(1, 5)]
        trend_bucket_count = 4
        trend_values = [0] * trend_bucket_count
        trend_scores = [[] for _ in range(trend_bucket_count)]
        bucket_seconds = max((current_end - current_start).total_seconds() / trend_bucket_count, 1)
    elif selected_range == "6m":
        current_start = _shift_months_preserving_day(now, -6)
        current_end = now
        previous_start = _shift_months_preserving_day(current_start, -6)
        previous_end = current_start
        compare_label = "vs previous 6 months"

        current_month_start = _month_start(current_start)
        trend_month_starts = [_add_months(current_month_start, idx) for idx in range(6)]
        trend_labels = [item.strftime("%b") for item in trend_month_starts]
        trend_bucket_count = 6
        trend_values = [0] * trend_bucket_count
        trend_scores = [[] for _ in range(trend_bucket_count)]
        bucket_seconds = None
    else:
        current_start = None
        current_end = None
        compare_label = "vs previous period"

        oldest_attempt = attempts_all_qs.order_by("started_at").first()
        current_month = _month_start(now)
        if oldest_attempt:
            oldest_month = _month_start(oldest_attempt.started_at)
            month_span = (current_month.year - oldest_month.year) * 12 + (current_month.month - oldest_month.month) + 1
            trend_bucket_count = max(1, min(6, month_span))
        else:
            trend_bucket_count = 6

        trend_start_month = _add_months(current_month, -(trend_bucket_count - 1))
        trend_month_starts = [_add_months(trend_start_month, idx) for idx in range(trend_bucket_count)]
        trend_labels = [item.strftime("%b") for item in trend_month_starts]
        trend_values = [0] * trend_bucket_count
        trend_scores = [[] for _ in range(trend_bucket_count)]
        bucket_seconds = None

    current_attempts_qs = filter_attempts_in_window(attempts_all_qs, current_start, current_end)
    current_metrics = build_metrics(current_attempts_qs)

    if previous_start is not None and previous_end is not None:
        previous_attempts_qs = filter_attempts_in_window(attempts_all_qs, previous_start, previous_end)
        previous_metrics = build_metrics(previous_attempts_qs)
    else:
        previous_metrics = {
            "avg_score_raw": current_metrics["avg_score_raw"],
            "avg_time_q": current_metrics["avg_time_q"],
            "accuracy_pct": current_metrics["accuracy_pct"],
            "sessions_count": current_metrics["sessions_count"],
        }

    current_attempts = current_metrics["attempts"]
    if selected_range == "30d":
        for attempt in current_attempts:
            if attempt.score is None:
                continue
            offset_seconds = (attempt.started_at - current_start).total_seconds()
            bucket_index = int(offset_seconds // bucket_seconds) if bucket_seconds else 0
            bucket_index = max(0, min(bucket_index, trend_bucket_count - 1))
            trend_scores[bucket_index].append(_pct_from_score_30(attempt.score))
    elif selected_range == "6m":
        trend_start = _month_start(current_start)
        for attempt in current_attempts:
            if attempt.score is None:
                continue
            local_started = timezone.localtime(attempt.started_at)
            bucket_index = (local_started.year - trend_start.year) * 12 + (local_started.month - trend_start.month)
            if 0 <= bucket_index < trend_bucket_count:
                trend_scores[bucket_index].append(_pct_from_score_30(attempt.score))
    else:
        trend_start = _add_months(_month_start(now), -(trend_bucket_count - 1))
        for attempt in current_attempts:
            if attempt.score is None:
                continue
            local_started = timezone.localtime(attempt.started_at)
            bucket_index = (local_started.year - trend_start.year) * 12 + (local_started.month - trend_start.month)
            if 0 <= bucket_index < trend_bucket_count:
                trend_scores[bucket_index].append(_pct_from_score_30(attempt.score))

    for idx, bucket in enumerate(trend_scores):
        if bucket:
            trend_values[idx] = int(round(sum(bucket) / len(bucket)))

    area_path, line_path = _build_trend_paths(trend_values)

    type_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    for ans in current_metrics["answers_qs"]:
        qtype = _question_type_label(ans.question.question_type if ans.question_id else "")
        type_stats[qtype]["total"] += 1
        if ans.is_correct:
            type_stats[qtype]["correct"] += 1

    by_type = []
    palette = ["bg-primary", "bg-primary-600", "bg-warning", "bg-accent-orange"]
    for idx, (label, item) in enumerate(type_stats.items()):
        pct = int(round((item["correct"] / item["total"]) * 100)) if item["total"] else 0
        by_type.append({"label": label, "pct": pct, "dot_class": palette[idx % len(palette)]})
    by_type.sort(key=lambda x: x["pct"], reverse=True)
    by_type = by_type[:4]

    history_rows = []
    for item in current_attempts[:8]:
        history_rows.append({
            "date": timezone.localtime(item.started_at).strftime("%b %d, %Y"),
            "mode": item.test.mode.title(),
            "score": f"{_score_to_30(item.score)}/30",
            "time_taken": _format_time_compact(item.total_time or 0),
            "detail_url": f"/team15/exam-result/?attempt_id={item.id}",
        })

    top_label = by_type[0]["label"] if by_type else "Reading"
    top_pct = by_type[0]["pct"] if by_type else 0
    low_label = by_type[-1]["label"] if by_type else "Reading"
    low_pct = by_type[-1]["pct"] if by_type else 0

    score_delta_raw = _percent_change(current_metrics["avg_score_raw"], previous_metrics["avg_score_raw"])
    time_delta_raw = current_metrics["avg_time_q"] - previous_metrics["avg_time_q"]
    accuracy_delta_raw = current_metrics["accuracy_pct"] - previous_metrics["accuracy_pct"]
    sessions_delta_raw = current_metrics["sessions_count"] - previous_metrics["sessions_count"]

    return {
        "progress_range": selected_range,
        "progress_avg_score": f"{int(round(current_metrics['avg_score_raw']))}/30",
        "progress_avg_time": _format_time_compact(current_metrics["avg_time_q"]),
        "progress_accuracy": f"{current_metrics['accuracy_pct']}%",
        "progress_total_sessions": current_metrics["sessions_count"],
        "progress_trend_value": f"{current_metrics['accuracy_pct']}%",
        "progress_trend_delta": _signed_percent(accuracy_delta_raw),
        "progress_trend_compare_label": compare_label,
        "progress_trend_area_path": area_path,
        "progress_trend_line_path": line_path,
        "progress_trend_labels": trend_labels,
        "progress_by_type": by_type,
        "progress_history_rows": history_rows,
        "progress_strength_label": top_label,
        "progress_strength_pct": top_pct,
        "progress_improve_label": low_label,
        "progress_improve_pct": low_pct,
        "progress_avg_score_delta": _signed_percent(score_delta_raw),
        "progress_avg_time_delta": _signed_seconds(time_delta_raw),
        "progress_accuracy_delta": _signed_percent(accuracy_delta_raw),
        "progress_total_sessions_delta": _signed_int(sessions_delta_raw),
        "progress_avg_score_delta_class": delta_class(score_delta_raw, positive_good=True),
        "progress_avg_time_delta_class": delta_class(time_delta_raw, positive_good=False),
        "progress_accuracy_delta_class": delta_class(accuracy_delta_raw, positive_good=True),
        "progress_total_sessions_delta_class": delta_class(sessions_delta_raw, positive_good=True),
        "progress_trend_delta_class": delta_class(accuracy_delta_raw, positive_good=True),
        "progress_trend_insight": f"Compared with {compare_label.replace('vs ', 'the ')}, your accuracy changed by {_signed_percent(accuracy_delta_raw)}.",
    }


def _exam_review_context(user, request):
    user_id = str(user.id)
    attempt_id = request.GET.get("attempt_id")
    question_id = request.GET.get("question_id")

    if not attempt_id or not question_id:
        return {
            "review_found": False,
            "review_back_url": "/team15/exam-result/",
            "review_error_message": "Question review is unavailable.",
            "review_question_type": "",
            "review_question_text": "",
            "review_passage_title": "",
            "review_passage_text": "",
            "review_selected_answer": "",
            "review_correct_answer": "",
        }

    answer = (
        Answer.objects.select_related("attempt", "question", "question__passage")
        .filter(
            attempt_id=attempt_id,
            attempt__user_id=user_id,
            attempt__status="completed",
            question_id=question_id,
        )
        .first()
    )

    if answer is None:
        return {
            "review_found": False,
            "review_back_url": f"/team15/exam-result/?attempt_id={attempt_id}",
            "review_error_message": "Question review is unavailable.",
            "review_question_type": "",
            "review_question_text": "",
            "review_passage_title": "",
            "review_passage_text": "",
            "review_selected_answer": "",
            "review_correct_answer": "",
        }

    passage = answer.question.passage if answer.question_id else None
    return {
        "review_found": True,
        "review_back_url": f"/team15/exam-result/?attempt_id={attempt_id}",
        "review_error_message": "",
        "review_question_type": _question_type_label(answer.question.question_type if answer.question_id else ""),
        "review_question_text": answer.question.question_text if answer.question_id else "",
        "review_passage_title": passage.title if passage else "",
        "review_passage_text": passage.content if passage else "",
        "review_selected_answer": answer.selected_answer,
        "review_correct_answer": answer.question.correct_answer if answer.question_id else "",
    }


def base(request):
    return dashboard_page(request)


@_page_login_required
def dashboard_page(request):
    context = {"user_id": str(request.user.id)}
    context.update(_dashboard_context(request.user))
    return render(request, f"{TEAM_NAME}/dashboard.html", context)


@_page_login_required
def exam_setup_page(request):
    context = {"user_id": str(request.user.id)}
    context.update(_exam_setup_context())
    return render(request, f"{TEAM_NAME}/exam_setup.html", context)


@_page_login_required
def exam_reading_page(request):
    context = {"user_id": str(request.user.id)}
    context.update(_exam_reading_context(request.user, request))
    return render(request, f"{TEAM_NAME}/exam_reading.html", context)


@_page_login_required
def practice_reading_page(request):
    context = {"user_id": str(request.user.id)}
    context.update(_practice_context(request.user, request))
    return render(request, f"{TEAM_NAME}/practice_reading.html", context)


@_page_login_required
def exam_result_page(request):
    context = {"user_id": str(request.user.id)}
    context.update(_exam_result_context(request.user, request))
    return render(request, f"{TEAM_NAME}/exam_result.html", context)


@_page_login_required
def exam_review_page(request):
    context = {"user_id": str(request.user.id)}
    context.update(_exam_review_context(request.user, request))
    return render(request, f"{TEAM_NAME}/exam_review.html", context)


@_page_login_required
def progress_tracking_page(request):
    context = {"user_id": str(request.user.id)}
    context.update(_progress_context(request.user, request))
    return render(request, f"{TEAM_NAME}/progress_tracking.html", context)


def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@_api_login_required
def test_list(request):
    qs = Test.objects.filter(is_active=True)
    mode = request.query_params.get("mode")
    if mode in ("exam", "practice"):
        qs = qs.filter(mode=mode)
    serializer = TestListSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@_api_login_required
def test_detail(request, test_id):
    try:
        test = Test.objects.get(id=test_id, is_active=True)
    except Test.DoesNotExist:
        return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = TestDetailSerializer(test)
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
@_api_login_required
def start_attempt(request):
    serializer = StartAttemptSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    test_id = serializer.validated_data["test_id"]
    user_id = _get_user_id(request, serializer.validated_data)

    if not user_id:
        return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        test = Test.objects.get(id=test_id, is_active=True)
    except Test.DoesNotExist:
        return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

    attempt = TestAttempt.objects.filter(
        test=test, user_id=user_id, status="in_progress"
    ).first()

    if attempt is None:
        attempt = TestAttempt.objects.create(test=test, user_id=user_id)

    return Response({
        "attempt_id": attempt.id,
        "test_id": test.id,
        "status": attempt.status,
        "started_at": attempt.started_at,
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
@_api_login_required
def submit_answer_practice(request):
    serializer = SubmitAnswerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    attempt_id = serializer.validated_data["attempt_id"]
    question_id = serializer.validated_data["question_id"]
    selected = serializer.validated_data["selected_answer"]
    time_spent = serializer.validated_data.get("time_spent")

    user_id = _get_user_id(request)

    try:
        attempt = TestAttempt.objects.get(id=attempt_id, user_id=user_id, status="in_progress")
    except TestAttempt.DoesNotExist:
        return Response({"detail": "Attempt not found or already completed."},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response({"detail": "Question not found."},
                        status=status.HTTP_404_NOT_FOUND)

    existing_answer = Answer.objects.filter(attempt=attempt, question=question).first()
    if existing_answer is not None:
        return Response({
            "answer_id": existing_answer.id,
            "is_correct": existing_answer.is_correct,
            "correct_answer": question.correct_answer,
            "selected_answer": existing_answer.selected_answer,
            "locked": True,
        })

    is_correct = selected.strip() == question.correct_answer.strip()
    normalized_time = max(1, int(time_spent)) if time_spent is not None else None

    answer = Answer.objects.create(
        attempt=attempt,
        question=question,
        selected_answer=selected,
        is_correct=is_correct,
        time_spent=normalized_time,
    )

    return Response({
        "answer_id": answer.id,
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "selected_answer": selected,
        "locked": True,
    })


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
@_api_login_required
def submit_exam(request):
    serializer = SubmitExamSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    attempt_id = serializer.validated_data["attempt_id"]
    answers_data = serializer.validated_data["answers"]

    user_id = _get_user_id(request)

    try:
        attempt = TestAttempt.objects.get(id=attempt_id, user_id=user_id, status="in_progress")
    except TestAttempt.DoesNotExist:
        return Response({"detail": "Attempt not found or already completed."},
                        status=status.HTTP_404_NOT_FOUND)

    test_question_ids = set(
        Question.objects.filter(passage__test=attempt.test).values_list("id", flat=True)
    )

    correct_count = 0
    total_questions = len(test_question_ids)

    for ans in answers_data:
        qid = ans["question_id"]
        if qid not in test_question_ids:
            continue

        try:
            question = Question.objects.get(id=qid)
        except Question.DoesNotExist:
            continue

        selected_answer = str(ans.get("selected_answer") or "").strip()
        is_correct = selected_answer == question.correct_answer.strip()
        if is_correct:
            correct_count += 1

        incoming_time = ans.get("time_spent")
        normalized_time = max(1, int(incoming_time)) if incoming_time is not None else None

        Answer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                "selected_answer": selected_answer,
                "is_correct": is_correct,
                "time_spent": normalized_time,
            },
        )

    score = calculate_score(correct_count, total_questions)
    accuracy = calculate_accuracy(correct_count, total_questions)

    now = timezone.now()
    attempt.status = "completed"
    attempt.score = score
    attempt.total_time = int((now - attempt.started_at).total_seconds())
    attempt.finished_at = now
    attempt.save()

    return Response({
        "attempt_id": attempt.id,
        "score": score,
        "accuracy": accuracy,
        "correct": correct_count,
        "total": total_questions,
        "status": "completed",
    })


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
@_api_login_required
def finish_practice(request):
    serializer = FinishPracticeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    attempt_id = serializer.validated_data["attempt_id"]

    user_id = _get_user_id(request)

    try:
        attempt = TestAttempt.objects.get(id=attempt_id, user_id=user_id, status="in_progress")
    except TestAttempt.DoesNotExist:
        return Response({"detail": "Attempt not found or already completed."},
                        status=status.HTTP_404_NOT_FOUND)

    answers = attempt.answers.all()
    correct_count = answers.filter(is_correct=True).count()
    total_questions = Question.objects.filter(passage__test=attempt.test).count()

    score = calculate_score(correct_count, total_questions)
    accuracy = calculate_accuracy(correct_count, total_questions)

    now = timezone.now()
    attempt.status = "completed"
    attempt.score = score
    attempt.total_time = int((now - attempt.started_at).total_seconds())
    attempt.finished_at = now
    attempt.save()

    return Response({
        "attempt_id": attempt.id,
        "score": score,
        "accuracy": accuracy,
        "correct": correct_count,
        "total": total_questions,
        "status": "completed",
    })


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@_api_login_required
def attempt_result(request, attempt_id):
    user_id = _get_user_id(request)

    try:
        attempt = TestAttempt.objects.select_related("test").prefetch_related(
            "answers__question"
        ).get(id=attempt_id, user_id=user_id)
    except TestAttempt.DoesNotExist:
        return Response({"detail": "Attempt not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = AttemptResultSerializer(attempt)
    data = serializer.data

    answers = attempt.answers.all()
    correct_count = answers.filter(is_correct=True).count()
    total_questions = Question.objects.filter(passage__test=attempt.test).count()
    data["accuracy"] = calculate_accuracy(correct_count, total_questions)
    data["correct"] = correct_count
    data["total"] = total_questions

    return Response(data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@_api_login_required
def user_history(request):
    user_id = _get_user_id(request)
    if not user_id:
        return Response({"detail": "user_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    attempts = TestAttempt.objects.filter(user_id=user_id).select_related("test").order_by("-started_at")
    serializer = AttemptHistorySerializer(attempts, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@_api_login_required
def user_dashboard(request):
    user_id = _get_user_id(request)
    if not user_id:
        return Response({"detail": "user_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    attempts = TestAttempt.objects.filter(user_id=user_id)
    completed = attempts.filter(status="completed")

    stats = completed.aggregate(
        avg_score=Avg("score"),
        total_attempts=Count("id"),
    )

    return Response({
        "user_id": user_id,
        "total_attempts": attempts.count(),
        "completed_attempts": completed.count(),
        "in_progress_attempts": attempts.filter(status="in_progress").count(),
        "average_score": round(stats["avg_score"], 1) if stats["avg_score"] else None,
    })
