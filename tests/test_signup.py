"""
Tests for POST /activities/{activity_name}/signup endpoint

Uses AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and client
- Act: Call the endpoint
- Assert: Verify response and state
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture to provide TestClient instance"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test"""
    # Save original state
    original_activities = {
        name: {
            "description": data["description"],
            "schedule": data["schedule"],
            "max_participants": data["max_participants"],
            "participants": data["participants"].copy()
        }
        for name, data in activities.items()
    }
    
    yield
    
    # Restore original state after test
    for name, data in activities.items():
        data["participants"] = original_activities[name]["participants"].copy()


def test_signup_new_participant_success(client):
    """
    Test successful signup of a new participant
    
    Arrange: Reset activities, prepare email that's not yet signed up
    Act: POST /activities/Chess Club/signup with new email
    Assert: Response is 200, participant added to activity
    """
    # Arrange
    activity_name = "Chess Club"
    new_email = "newemail@mergington.edu"
    
    # Get initial participant count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity_name]["participants"])
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    
    # Verify participant was added
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()[activity_name]["participants"])
    assert updated_count == initial_count + 1
    assert new_email in updated_response.json()[activity_name]["participants"]


def test_signup_duplicate_participant_fails(client):
    """
    Test signup fails when participant already registered
    
    Arrange: Get existing participant from an activity
    Act: Try to signup the same participant again
    Assert: Response is 400 with appropriate error message
    """
    # Arrange
    activity_name = "Chess Club"
    existing_response = client.get("/activities")
    existing_participant = existing_response.json()[activity_name]["participants"][0]
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_participant}
    )
    
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity_fails(client):
    """
    Test signup fails for non-existent activity
    
    Arrange: Prepare a non-existent activity name
    Act: Try to signup for non-existent activity
    Assert: Response is 404 with error message
    """
    # Arrange
    fake_activity = "Fake Activity That Does Not Exist"
    email = "test@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{fake_activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_email_required(client):
    """
    Test signup fails when email parameter is missing
    
    Arrange: Prepare request without email parameter
    Act: POST to signup endpoint without email
    Assert: Response is 422 (validation error)
    """
    # Arrange
    activity_name = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup")
    
    # Assert
    assert response.status_code == 422


def test_signup_activity_name_case_sensitive(client):
    """
    Test signup with different case for activity name
    
    Arrange: Use different case for activity name
    Act: POST to signup with different case
    Assert: Response is 404 (activity not found due to case sensitivity)
    """
    # Arrange
    activity_name = "chess club"  # lowercase
    email = "test@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404


def test_signup_special_characters_in_email(client):
    """
    Test signup with email containing special characters
    
    Arrange: Prepare email with special characters
    Act: POST to signup with special characters in email
    Assert: Response is 200 (special characters should be handled)
    """
    # Arrange
    activity_name = "Chess Club"
    email = "test+filter@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200


def test_signup_response_contains_message(client):
    """
    Test that signup response contains success message
    
    Arrange: Prepare valid signup request
    Act: POST to signup endpoint
    Assert: Response body contains message field with expected format
    """
    # Arrange
    activity_name = "Programming Class"
    email = "testuser@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert email in response_data["message"]
    assert activity_name in response_data["message"]
