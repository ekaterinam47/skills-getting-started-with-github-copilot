"""
Tests for GET /activities endpoint

Uses AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and client
- Act: Call the endpoint
- Assert: Verify response
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide TestClient instance"""
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    """
    Test that GET /activities returns all activities
    
    Arrange: Client is ready
    Act: Make GET request to /activities
    Assert: Response status is 200 and contains expected activities
    """
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    
    # Verify response is a dictionary
    assert isinstance(activities, dict)
    
    # Verify expected activities are present
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities


def test_get_activities_returns_activity_details(client):
    """
    Test that activity objects contain required fields
    
    Arrange: Client is ready
    Act: Make GET request to /activities
    Assert: Each activity has description, schedule, max_participants, participants
    """
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        # Verify types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_get_activities_participants_are_valid_emails(client):
    """
    Test that participant list contains valid email strings
    
    Arrange: Client is ready
    Act: Make GET request to /activities
    Assert: All participants have valid email format
    """
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name, activity_data in activities.items():
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant
            assert "." in participant


def test_get_activities_max_participants_positive(client):
    """
    Test that max_participants is a positive integer
    
    Arrange: Client is ready
    Act: Make GET request to /activities
    Assert: All activities have positive max_participants
    """
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name, activity_data in activities.items():
        assert activity_data["max_participants"] > 0
