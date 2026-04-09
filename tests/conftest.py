"""Pytest configuration and fixtures for the Mergington High School API."""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Provide a sample email for testing."""
    return "test@mergington.edu"


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store original state
    original_activities = {
        key: {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }
        for key, value in activities.items()
    }

    yield

    # Restore original state after test
    activities.clear()
    activities.update(original_activities)