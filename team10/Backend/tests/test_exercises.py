"""Unit tests for exercise API endpoints."""
import pytest
from fastapi import status


def test_get_exercises_requires_auth(client):
    """Test getting exercises without authentication returns 401."""
    response = client.get("/api/exercises/listening")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_submit_exercise_requires_auth(client):
    """Test submitting exercise without authentication returns 401."""
    response = client.post("/api/exercises/listening/submit", json={
        "exerciseId": "1",
        "answers": []
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_submit_exercise_validation(client):
    """Test exercise submission with invalid data returns validation error."""
    response = client.post("/api/exercises/listening/submit", json={
        "exerciseId": "invalid",
        "answers": "not-an-array"
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
