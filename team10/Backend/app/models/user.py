"""User database model and data access operations."""
from typing import Optional, Dict, Any
from datetime import datetime
import pyodbc


class User:
    """Represents a user entity with database operations."""
    
    def __init__(
        self,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
        role: str = "student",
        full_name: Optional[str] = None,
        level: Optional[str] = None,
        preferences: Optional[str] = None,
        last_login_at: Optional[datetime] = None,
        phone_verified: bool = False,
        email_verified: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_deleted: bool = False
    ):
        """Initialize user instance with attributes."""
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.level = level
        self.preferences = preferences
        self.last_login_at = last_login_at
        self.phone_verified = phone_verified
        self.email_verified = email_verified
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_deleted = is_deleted
    
    @staticmethod
    def from_db_row(row: pyodbc.Row) -> 'User':
        """Create User instance from database row."""
        return User(
            user_id=row.user_id,
            email=row.email,
            password_hash=row.password_hash,
            role=row.role,
            full_name=row.full_name,
            level=row.level,
            preferences=row.preferences,
            last_login_at=row.last_login_at,
            phone_verified=row.phone_verified,
            email_verified=row.email_verified,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_deleted=row.is_deleted
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user instance to dictionary."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "level": self.level,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "created_at": self.created_at
        }
