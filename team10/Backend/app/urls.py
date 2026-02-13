"""URL routing configuration for the application."""
from fastapi import APIRouter
from app.api import users, exercises

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])

# Route mapping documentation
ROUTE_MAP = {
    "authentication": {
        "register": "POST /api/users/register",
        "login": "POST /api/users/login",
        "logout": "POST /api/users/logout",
    },
    "users": {
        "update_profile": "PUT /api/users/{userId}/profile",
        "completed_exercises": "GET /api/users/{userId}/exercises/completed",
        "mark_complete": "PUT /api/users/{userId}/exercises/{exerciseId}/complete",
    },
    "exercises": {
        "list_listening": "GET /api/exercises/listening",
        "get_by_id": "GET /api/exercises/{exerciseId}",
        "submit": "POST /api/exercises/listening/submit",
        "post_results": "POST /api/exercises/{exerciseId}/results",
        "post_comment": "POST /api/exercises/{exerciseId}/comments",
        "get_reviews": "GET /api/exercises/{exerciseId}/reviews",
        "post_review": "POST /api/exercises/{exerciseId}/reviews",
    }
}
