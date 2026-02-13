"""User service handling business logic for user operations."""
from typing import Optional
from datetime import datetime
import pyodbc
from app.models.user import User
from app.core.security import security_service


class UserService:
    """Handles user-related business logic and database operations."""
    
    @staticmethod
    def create_user(cursor: pyodbc.Cursor, email: str, password: str, 
                   full_name: str, username: str) -> User:
        """Create a new user in the database."""
        password_hash = security_service.get_password_hash(password)
        
        query = """
            INSERT INTO users (email, password_hash, role, full_name, 
                             phone_verified, email_verified, created_at)
            OUTPUT INSERTED.*
            VALUES (?, ?, 'student', ?, 0, 0, ?)
        """
        
        cursor.execute(query, (email, password_hash, full_name or username, 
                              datetime.utcnow()))
        row = cursor.fetchone()
        return User.from_db_row(row)
    
    @staticmethod
    def get_user_by_email(cursor: pyodbc.Cursor, email: str) -> Optional[User]:
        """Retrieve user by email address."""
        query = """
            SELECT * FROM users 
            WHERE email = ? AND is_deleted = 0
        """
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        return User.from_db_row(row) if row else None
    
    @staticmethod
    def get_user_by_id(cursor: pyodbc.Cursor, user_id: int) -> Optional[User]:
        """Retrieve user by user ID."""
        query = """
            SELECT * FROM users 
            WHERE user_id = ? AND is_deleted = 0
        """
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        return User.from_db_row(row) if row else None
    
    @staticmethod
    def update_last_login(cursor: pyodbc.Cursor, user_id: int) -> None:
        """Update user's last login timestamp."""
        query = """
            UPDATE users 
            SET last_login_at = ? 
            WHERE user_id = ?
        """
        cursor.execute(query, (datetime.utcnow(), user_id))
    
    @staticmethod
    def update_user_profile(cursor: pyodbc.Cursor, user_id: int, 
                           name: Optional[str] = None,
                           email: Optional[str] = None,
                           bio: Optional[str] = None,
                           level: Optional[str] = None) -> Optional[User]:
        """Update user profile information."""
        updates = []
        params = []
        
        if name:
            updates.append("full_name = ?")
            params.append(name)
        if email:
            updates.append("email = ?")
            params.append(email)
        if level:
            updates.append("level = ?")
            params.append(level)
        if bio:
            updates.append("preferences = ?")
            params.append(bio)
        
        if not updates:
            return UserService.get_user_by_id(cursor, user_id)
        
        updates.append("updated_at = ?")
        params.append(datetime.utcnow())
        params.append(user_id)
        
        query = f"""
            UPDATE users 
            SET {', '.join(updates)}
            WHERE user_id = ?
        """
        
        cursor.execute(query, params)
        return UserService.get_user_by_id(cursor, user_id)
    
    @staticmethod
    def verify_password(user: User, password: str) -> bool:
        """Verify user password against stored hash."""
        return security_service.verify_password(password, user.password_hash)


user_service = UserService()
