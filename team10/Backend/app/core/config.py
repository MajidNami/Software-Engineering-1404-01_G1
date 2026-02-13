"""Environment configuration settings for the application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    DB_SERVER: str = "localhost"
    DB_NAME: str = "ToeflListeningDb"
    DB_USER: str = "sa"
    DB_PASSWORD: str = "YourPassword123"
    DB_DRIVER: str = "{ODBC Driver 17 for SQL Server}"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    ALLOWED_ORIGINS: list = ["http://localhost:4200"]
    
    # Application settings
    PROJECT_NAME: str = "TOEFL Listening API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    class Config:
        """Pydantic configuration class."""
        env_file = ".env"
        case_sensitive = True


settings = Settings()
