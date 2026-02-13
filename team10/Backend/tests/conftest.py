"""Test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client for API testing."""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Provide test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }


@pytest.fixture
def test_login_data():
    """Provide test login data."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
