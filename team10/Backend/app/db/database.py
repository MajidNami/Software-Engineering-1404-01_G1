"""Database connection and session management."""
import pyodbc
from typing import Generator
from contextlib import contextmanager
from app.core.config import settings


class DatabaseConnection:
    """Manages database connections and provides connection pooling."""
    
    def __init__(self):
        """Initialize database connection parameters."""
        self.connection_string = (
            f"DRIVER={settings.DB_DRIVER};"
            f"SERVER={settings.DB_SERVER};"
            f"DATABASE={settings.DB_NAME};"
            f"UID={settings.DB_USER};"
            f"PWD={settings.DB_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
    
    def get_connection(self) -> pyodbc.Connection:
        """Create and return a new database connection."""
        return pyodbc.connect(self.connection_string)
    
    @contextmanager
    def get_cursor(self) -> Generator[pyodbc.Cursor, None, None]:
        """Provide a transactional scope for database operations."""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()


db = DatabaseConnection()


def get_db() -> Generator[pyodbc.Cursor, None, None]:
    """Dependency for FastAPI routes to get database cursor."""
    with db.get_cursor() as cursor:
        yield cursor
