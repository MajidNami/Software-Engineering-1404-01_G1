from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Avg, Count
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .models import Test, Passage, Question, TestAttempt, Answer
from .serializers import (
    TestListSerializer, TestDetailSerializer,
    StartAttemptSerializer, SubmitAnswerSerializer,
    SubmitExamSerializer, FinishPracticeSerializer,
    AttemptResultSerializer, AttemptHistorySerializer,
)
from .scoring import calculate_score, calculate_accuracy

TEAM_NAME = "team15"


def _get_user_id(request, data=None):
    """Get user_id from authenticated user, or fallback to request data/query param."""
    if hasattr(request, 'user') and hasattr(request.user, 'id') and request.user.is_authenticated:
        return str(request.user.id)
    if data and data.get("user_id"):
        return data["user_id"]
    user_id = request.query_params.get("user_id") if hasattr(request, 'query_params') else request.GET.get("user_id")
    return user_id


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


# ─── API Views ───────────────────────────────────────────────


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def test_list(request):
    """List active tests. Optional filter: ?mode=exam or ?mode=practice"""
    qs = Test.objects.filter(is_active=True)
    mode = request.query_params.get("mode")
    if mode in ("exam", "practice"):
        qs = qs.filter(mode=mode)
    serializer = TestListSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def test_detail(request, test_id):
    """Get a test with its passages and questions."""
    try:
        test = Test.objects.get(id=test_id, is_active=True)
    except Test.DoesNotExist:
        return Response({"detail": "Test not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = TestDetailSerializer(test)
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def start_attempt(request):
    """Start a new attempt or resume an in-progress one."""
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

    # Resume existing in-progress attempt if one exists
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
def submit_answer_practice(request):
    """Submit a single answer in practice mode. Returns immediate feedback."""
    serializer = SubmitAnswerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    attempt_id = serializer.validated_data["attempt_id"]
    question_id = serializer.validated_data["question_id"]
    selected = serializer.validated_data["selected_answer"]
    time_spent = serializer.validated_data.get("time_spent")

    user_id = _get_user_id(request)

    try:
        lookup = {"id": attempt_id, "status": "in_progress"}
        if user_id:
            lookup["user_id"] = user_id
        attempt = TestAttempt.objects.get(**lookup)
    except TestAttempt.DoesNotExist:
        return Response({"detail": "Attempt not found or already completed."},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response({"detail": "Question not found."},
                        status=status.HTTP_404_NOT_FOUND)

    is_correct = selected.strip() == question.correct_answer.strip()

    answer, created = Answer.objects.update_or_create(
        attempt=attempt,
        question=question,
        defaults={
            "selected_answer": selected,
            "is_correct": is_correct,
            "time_spent": time_spent,
        },
    )

    return Response({
        "answer_id": answer.id,
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "selected_answer": selected,
    })


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def submit_exam(request):
    """Bulk submit all answers for an exam attempt, then score it."""
    serializer = SubmitExamSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    attempt_id = serializer.validated_data["attempt_id"]
    answers_data = serializer.validated_data["answers"]

    user_id = _get_user_id(request)

    try:
        lookup = {"id": attempt_id, "status": "in_progress"}
        if user_id:
            lookup["user_id"] = user_id
        attempt = TestAttempt.objects.get(**lookup)
    except TestAttempt.DoesNotExist:
        return Response({"detail": "Attempt not found or already completed."},
                        status=status.HTTP_404_NOT_FOUND)

    # Collect all question IDs for this test
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

        is_correct = ans["selected_answer"].strip() == question.correct_answer.strip()
        if is_correct:
            correct_count += 1

        Answer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                "selected_answer": ans["selected_answer"],
                "is_correct": is_correct,
                "time_spent": ans.get("time_spent"),
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
def finish_practice(request):
    """Finalize a practice attempt and calculate score."""
    serializer = FinishPracticeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    attempt_id = serializer.validated_data["attempt_id"]

    user_id = _get_user_id(request)

    try:
        lookup = {"id": attempt_id, "status": "in_progress"}
        if user_id:
            lookup["user_id"] = user_id
        attempt = TestAttempt.objects.get(**lookup)
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
def attempt_result(request, attempt_id):
    """Get detailed results for an attempt."""
    user_id = _get_user_id(request)

    try:
        lookup = {"id": attempt_id}
        if user_id:
            lookup["user_id"] = user_id
        attempt = TestAttempt.objects.select_related("test").prefetch_related(
            "answers__question"
        ).get(**lookup)
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
def user_history(request):
    """Get attempt history. Uses authenticated user or ?user_id= query param."""
    user_id = _get_user_id(request)
    if not user_id:
        return Response({"detail": "user_id query parameter is required."},
                        status=status.HTTP_400_BAD_REQUEST)

    attempts = TestAttempt.objects.filter(user_id=user_id).select_related("test").order_by("-started_at")
    serializer = AttemptHistorySerializer(attempts, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def user_dashboard(request):
    """Aggregated stats. Uses authenticated user or ?user_id= query param."""
    user_id = _get_user_id(request)
    if not user_id:
        return Response({"detail": "user_id query parameter is required."},
                        status=status.HTTP_400_BAD_REQUEST)

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
