"""Unit tests for user API endpoints."""
import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_api_root(client):
    """Test API root endpoint returns endpoint information."""
    response = client.get("/api")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "endpoints" in data
    assert "auth" in data["endpoints"]


def test_register_validation_error(client):
    """Test user registration with invalid data returns validation error."""
    response = client.post("/api/users/register", json={
        "email": "invalid-email",
        "password": "short"
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_validation_error(client):
    """Test user login with invalid credentials format."""
    response = client.post("/api/users/login", json={
        "email": "invalid-email",
        "password": ""
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
