"""User-related Pydantic schemas for request/response validation."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    level: Optional[str] = None
    preferences: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response data."""
    user_id: int
    email: str
    full_name: str
    role: str
    level: Optional[str] = None
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
