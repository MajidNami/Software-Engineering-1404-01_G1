"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.core.exceptions import validation_exception_handler, general_exception_handler
from app.core.logging import setup_logging
from app.api import users, exercises


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    # Setup logging
    setup_logging(debug=settings.DEBUG)
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Mount static files for audio
    static_path = Path(__file__).parent.parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    # Include routers
    app.include_router(users.router, prefix="/api")
    app.include_router(exercises.router, prefix="/api")
    
    return app


app = create_application()


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "TOEFL Listening API",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get("/api")
async def api_root():
    """API root endpoint with available endpoints."""
    return {
        "message": "TOEFL Listening API",
        "version": settings.VERSION,
        "endpoints": {
            "auth": {
                "register": "POST /api/users/register",
                "login": "POST /api/users/login",
                "logout": "POST /api/users/logout"
            },
            "users": {
                "profile": "PUT /api/users/{userId}/profile",
                "completed": "GET /api/users/{userId}/exercises/completed"
            },
            "exercises": {
                "list": "GET /api/exercises/listening",
                "detail": "GET /api/exercises/{exerciseId}",
                "submit": "POST /api/exercises/listening/submit",
                "complete": "PUT /api/users/{userId}/exercises/{exerciseId}/complete"
            }
        }
    }
