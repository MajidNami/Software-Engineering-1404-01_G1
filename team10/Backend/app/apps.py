"""Application configuration and metadata."""
from app.core.config import settings


class AppConfig:
    """Main application configuration class."""
    
    name = "toefl_listening"
    verbose_name = "TOEFL Listening Practice"
    version = settings.VERSION
    description = "Backend API for TOEFL Listening practice application"
    
    # Application metadata
    metadata = {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "API for managing TOEFL listening exercises and user progress",
        "contact": {
            "name": "Development Team",
            "email": "dev@toefllistening.com",
        },
        "license": {
            "name": "Private",
        },
    }
    
    # Feature flags
    features = {
        "authentication": True,
        "exercises": True,
        "analytics": True,
        "admin_panel": False,  # To be implemented
    }
    
    # API versioning
    api_version = "v1"
    api_prefix = "/api"


# Create singleton instance
app_config = AppConfig()
