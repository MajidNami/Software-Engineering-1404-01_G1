"""User authentication and profile management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
import pyodbc
from app.db.database import get_db
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserResponse, UserProfileUpdate
)
from app.schemas.base import TokenResponse, MessageResponse
from app.services.user_service import user_service
from app.core.security import security_service
from app.core.dependencies import get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegisterRequest,
    cursor: pyodbc.Cursor = Depends(get_db)
):
    """Register a new user account."""
    existing_user = user_service.get_user_by_email(cursor, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = user_service.create_user(
        cursor=cursor,
        email=request.email,
        password=request.password,
        full_name=request.full_name or request.username,
        username=request.username
    )
    
    return UserResponse(**user.to_dict())


@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: UserLoginRequest,
    cursor: pyodbc.Cursor = Depends(get_db)
):
    """Authenticate user and return JWT tokens."""
    user = user_service.get_user_by_email(cursor, request.email)
    
    if not user or not user_service.verify_password(user, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_service.update_last_login(cursor, user.user_id)
    
    access_token = security_service.create_access_token(data={"sub": str(user.user_id)})
    refresh_token = security_service.create_refresh_token(data={"sub": str(user.user_id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: User = Depends(get_current_active_user)
):
    """Logout current user (client should discard tokens)."""
    return MessageResponse(message="Successfully logged out")


@router.put("/{user_id}/profile", response_model=UserResponse)
async def update_user_profile(
    user_id: int,
    request: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    cursor: pyodbc.Cursor = Depends(get_db)
):
    """Update user profile information."""
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    updated_user = user_service.update_user_profile(
        cursor=cursor,
        user_id=user_id,
        name=request.name,
        email=request.email,
        bio=request.bio,
        level=request.level
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**updated_user.to_dict())
