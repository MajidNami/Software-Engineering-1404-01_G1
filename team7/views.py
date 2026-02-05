from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from core.auth import api_login_required
import json
import logging
from .models import Question, Evaluation, DetailedScore
from .services import EvaluationService

logger = logging.getLogger(__name__)
TEAM_NAME = "team7"


@api_login_required
def ping(request):
    """Health check endpoint per FR-API-01."""
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    """Serve team7 index page."""
    return render(request, f"{TEAM_NAME}/index.html")


@csrf_exempt
@require_http_methods(["POST"])
@api_login_required
def submit_writing(request):
    """Controller endpoint for writing submission (UC-01, FR-WR, FR-API-02).
    
    Expects JSON:
        {
            "user_id": "uuid",
            "question_id": "uuid",
            "text": "essay text..."
        }
    
    Returns JSON with evaluation result and detailed scores.
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        question_id = data.get('question_id')
        text = data.get('text', '').strip()

        # Input validation
        if not all([user_id, question_id, text]):
            logger.warning(f"Missing required fields in writing submission")
            return JsonResponse({
                "error": "INVALID_INPUT",
                "message": "Missing user_id, question_id, or text"
            }, status=400)

        # Call service orchestrator
        service = EvaluationService()
        result, status_code = service.evaluate_writing(user_id, question_id, text)

        return JsonResponse(result, status=status_code)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({
            "error": "INVALID_INPUT",
            "message": "Request body must be valid JSON"
        }, status=400)
    except Exception as e:
        logger.exception(f"Unexpected error in submit_writing: {str(e)}")
        return JsonResponse({
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }, status=500)


@require_http_methods(["GET"])
@api_login_required
def get_history(request, user_id=None):
    """Controller endpoint for student progress/history (UC-03).
    
    Returns list of past evaluations with scores and trends.
    """
    try:
        # Use request.user.id if available, else from query param
        if not user_id:
            user_id = request.GET.get('user_id') or str(request.user.id)

        service = EvaluationService()
        limit = int(request.GET.get('limit', 50))
        result, status_code = service.get_user_history(user_id, limit)

        return JsonResponse(result, status=status_code)

    except ValueError:
        logger.error(f"Invalid limit parameter: {request.GET.get('limit')}")
        return JsonResponse({
            "error": "INVALID_INPUT",
            "message": "limit must be an integer"
        }, status=400)
    except Exception as e:
        logger.exception(f"Error in get_history: {str(e)}")
        return JsonResponse({
            "error": "INTERNAL_ERROR",
            "message": "Failed to retrieve history"
        }, status=500)