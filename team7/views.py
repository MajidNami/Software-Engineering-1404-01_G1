from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from core.auth import api_login_required
import json
import logging
from django.db import connection
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .models import Question, Evaluation, DetailedScore, APILog
from .services import EvaluationService, AnalyticsService

logger = logging.getLogger(__name__)
TEAM_NAME = "team7"


@api_login_required
def ping(request):
    """Health check endpoint per FR-API-01."""
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def index(request):
    """Serve team7 home page (landing page)."""
    return render(request, f"{TEAM_NAME}/index.html")


def dashboard(request):
    """Serve team7 dashboard page (user dashboard)."""
    return render(request, f"{TEAM_NAME}/dashboard.html")


def exams(request):
    """Serve team7 exams page (exams listing and history)."""
    return render(request, f"{TEAM_NAME}/exam.html")


def writing_exam(request):
    """Serve team7 writing exam page (writing exam taking interface)."""
    return render(request, f"{TEAM_NAME}/writing-exam.html")


def speaking_exam(request):
    """Serve team7 speaking exam page (speaking exam taking interface)."""
    return render(request, f"{TEAM_NAME}/speaking-exam.html")


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


@csrf_exempt
@require_http_methods(["POST"])
@api_login_required
def submit_speaking(request):
    """Controller endpoint for speaking submission (UC-02, FR-SP, FR-API-02).
    
    Expects multipart/form-data:
        - user_id: UUID string
        - question_id: UUID string
        - audio_file: Audio file (.wav, .mp3, .flac)
    
    Returns JSON with evaluation result, transcript, and detailed scores.
    """
    try:
        # Extract form data
        user_id = request.POST.get('user_id')
        question_id = request.POST.get('question_id')
        
        # Input validation
        if not all([user_id, question_id]):
            logger.warning(f"Missing required fields in speaking submission")
            return JsonResponse({
                "error": "INVALID_INPUT",
                "message": "Missing user_id or question_id"
            }, status=400)

        # Check for audio file in request.FILES
        if 'audio_file' not in request.FILES:
            logger.warning(f"No audio file in request")
            return JsonResponse({
                "error": "INVALID_INPUT",
                "message": "Missing audio_file in request"
            }, status=400)

        audio_file = request.FILES['audio_file']
        
        # Log file info
        logger.info(f"Received speaking submission: user={user_id}, question={question_id}, file={audio_file.name}, size={audio_file.size} bytes")

        # Call service orchestrator
        service = EvaluationService()
        result, status_code = service.evaluate_speaking(
            user_id=user_id,
            question_id=question_id,
            audio_file=audio_file,
            audio_filename=audio_file.name
        )

        return JsonResponse(result, status=status_code)

    except Exception as e:
        logger.exception(f"Unexpected error in submit_speaking: {str(e)}")
        return JsonResponse({
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }, status=500)


@require_http_methods(["GET"])
@api_login_required
def get_analytics(request, user_id=None):
    """Controller endpoint for student analytics with trends (UC-03, FR-MON-02).
    
    Returns evaluation history with statistical analysis and trends.
    
    Query Parameters:
        - limit: Max number of records (default 50)
    
    Response includes:
        - attempts: List of evaluations
        - analytics: Overall, writing, and speaking statistics
            - statistics: mean, min, max, median, count
            - improvement: percentage change and trend direction
            - moving_average: 3-point moving average for smoothing
    """
    try:
        # Use request.user.id if available, else from query param
        if not user_id:
            user_id = request.GET.get('user_id') or str(request.user.id)

        analytics_service = AnalyticsService()
        limit = int(request.GET.get('limit', 50))
        result, status_code = analytics_service.get_user_analytics(user_id, limit)

        return JsonResponse(result, status=status_code)

    except ValueError:
        logger.error(f"Invalid limit parameter: {request.GET.get('limit')}")
        return JsonResponse({
            "error": "INVALID_INPUT",
            "message": "limit must be an integer"
        }, status=400)
    except Exception as e:
        logger.exception(f"Error in get_analytics: {str(e)}")
        return JsonResponse({
            "error": "INTERNAL_ERROR",
            "message": "Failed to retrieve analytics"
        }, status=500)


@require_http_methods(["GET"])
@api_login_required
def admin_health(request):
    """Admin endpoint for system health monitoring (UC-04, FR-MON, NFR-AVAIL-01).
    
    Checks:
        - Database connectivity
        - External AI service status (LLM)
        - Recent API performance metrics
        - Error rates
        - System uptime statistics
    
    Returns comprehensive health status for admin dashboard.
    """
    health_status = {
        "service": "team7",
        "timestamp": timezone.now().isoformat(),
        "status": "healthy",
        "checks": {}
    }

    # 1. Database Check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }
        logger.error(f"Database health check failed: {str(e)}")

    # 2. External AI Service Check (LLM)
    try:
        from django.conf import settings
        from openai import OpenAI
        
        client = OpenAI(
            api_key=getattr(settings, 'AI_GENERATOR_API_KEY', None),
            base_url="https://api.gpt4-all.xyz/v1"
        )
        
        # Quick ping to LLM service (with timeout)
        models = client.models.list()
        
        health_status["checks"]["llm_service"] = {
            "status": "healthy",
            "message": "LLM API accessible",
            "models_available": len(models.data) if hasattr(models, 'data') else 0
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["llm_service"] = {
            "status": "unhealthy",
            "message": f"LLM service error: {str(e)}"
        }
        logger.warning(f"LLM service health check failed: {str(e)}")

    # 3. API Performance Metrics (last 24 hours)
    try:
        yesterday = timezone.now() - timedelta(hours=24)
        recent_logs = APILog.objects.filter(timestamp__gte=yesterday)
        
        total_requests = recent_logs.count()
        error_requests = recent_logs.filter(status_code__gte=400).count()
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate average latency
        avg_latency = recent_logs.aggregate(
            avg_latency=models.Avg('latency_ms')
        )['avg_latency'] or 0
        
        # Get slowest endpoints
        slow_endpoints = recent_logs.values('endpoint').annotate(
            avg_latency=models.Avg('latency_ms'),
            count=models.Count('log_id')
        ).order_by('-avg_latency')[:5]
        
        health_status["checks"]["api_performance"] = {
            "status": "healthy" if error_rate < 10 and avg_latency < 5000 else "degraded",
            "total_requests_24h": total_requests,
            "error_requests_24h": error_requests,
            "error_rate": round(error_rate, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "slowest_endpoints": list(slow_endpoints)
        }
        
        # Update overall status based on error rate
        if error_rate > 25:
            health_status["status"] = "unhealthy"
        elif error_rate > 10:
            health_status["status"] = "degraded"
            
    except Exception as e:
        health_status["checks"]["api_performance"] = {
            "status": "unknown",
            "message": f"Unable to calculate metrics: {str(e)}"
        }
        logger.error(f"API performance check failed: {str(e)}")

    # 4. Database Statistics
    try:
        total_evaluations = Evaluation.objects.count()
        total_questions = Question.objects.count()
        evaluations_today = Evaluation.objects.filter(
            created_at__gte=timezone.now().date()
        ).count()
        
        health_status["checks"]["database_stats"] = {
            "status": "info",
            "total_evaluations": total_evaluations,
            "total_questions": total_questions,
            "evaluations_today": evaluations_today
        }
    except Exception as e:
        logger.error(f"Database stats check failed: {str(e)}")

    # Determine HTTP status code
    if health_status["status"] == "healthy":
        status_code = 200
    elif health_status["status"] == "degraded":
        status_code = 200  # Still operational
    else:
        status_code = 503  # Service Unavailable

    return JsonResponse(health_status, status=status_code)