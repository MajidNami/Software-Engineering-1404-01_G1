"""Base Pydantic schemas and response models."""
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel


T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Generic response wrapper for API endpoints."""
    success: bool
    message: str
    data: Optional[T] = None


class TokenResponse(BaseModel):
    """JWT token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Simple message response schema."""
    message: str
