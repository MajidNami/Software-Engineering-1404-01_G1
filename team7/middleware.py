"""
Middleware for Team7 API request logging and monitoring.

Automatically logs all API requests to the APILog model for
system health monitoring and performance analysis.
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from .models import APILog

logger = logging.getLogger(__name__)


class APILoggingMiddleware(MiddlewareMixin):
    """Middleware to log API requests for monitoring (FR-MON, UC-04).
    
    Captures:
        - Endpoint and HTTP method
        - Response status code
        - Processing latency
        - User ID (if authenticated)
        - Error messages (for failed requests)
    
    Usage:
        Add 'team7.middleware.APILoggingMiddleware' to MIDDLEWARE in settings.py
    """

    def process_request(self, request):
        """Mark the start time of the request."""
        request._start_time = time.time()
        return None

    def process_response(self, request, response):
        """Log the completed request to database."""
        # Only log team7 API endpoints
        if not request.path.startswith('/team7/api/'):
            return response

        # Calculate latency
        if hasattr(request, '_start_time'):
            latency_ms = int((time.time() - request._start_time) * 1000)
        else:
            latency_ms = 0

        # Extract user ID (if authenticated)
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = str(request.user.id)

        # Extract error message for failed requests
        error_message = None
        if response.status_code >= 400:
            try:
                # Try to extract error from JSON response
                if hasattr(response, 'content'):
                    import json
                    error_data = json.loads(response.content)
                    error_message = error_data.get('message', error_data.get('error', ''))
            except:
                error_message = f"HTTP {response.status_code}"

        # Get request and response sizes
        request_size = len(request.body) if hasattr(request, 'body') else None
        response_size = len(response.content) if hasattr(response, 'content') else None

        # Log to database (async to avoid blocking)
        try:
            APILog.objects.create(
                user_id=user_id,
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                latency_ms=latency_ms,
                error_message=error_message,
                request_size=request_size,
                response_size=response_size
            )
        except Exception as e:
            # Don't let logging errors break the request
            logger.error(f"Failed to log API request: {str(e)}")

        # Add latency header for debugging
        response['X-Response-Time'] = f"{latency_ms}ms"

        return response

    def process_exception(self, request, exception):
        """Log exceptions that occur during request processing."""
        if not request.path.startswith('/team7/api/'):
            return None

        # Calculate latency
        if hasattr(request, '_start_time'):
            latency_ms = int((time.time() - request._start_time) * 1000)
        else:
            latency_ms = 0

        # Extract user ID
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = str(request.user.id)

        # Log the exception
        try:
            APILog.objects.create(
                user_id=user_id,
                endpoint=request.path,
                method=request.method,
                status_code=500,  # Internal Server Error
                latency_ms=latency_ms,
                error_message=str(exception)
            )
        except Exception as e:
            logger.error(f"Failed to log API exception: {str(e)}")

        return None  # Let Django handle the exception normally
