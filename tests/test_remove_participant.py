"""
Tests for DELETE /activities/{activity_name}/participants/{email} endpoint

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


def test_remove_existing_participant_success(client):
    """
    Test successful removal of an existing participant
    
    Arrange: Get an existing participant from an activity
    Act: DELETE the participant from the activity
    Assert: Response is 200, participant removed from activity
    """
    # Arrange
    activity_name = "Chess Club"
    initial_response = client.get("/activities")
    participant_to_remove = initial_response.json()[activity_name]["participants"][0]
    initial_count = len(initial_response.json()[activity_name]["participants"])
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{participant_to_remove}"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant_to_remove} from {activity_name}"
    
    # Verify participant was removed
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()[activity_name]["participants"])
    assert updated_count == initial_count - 1
    assert participant_to_remove not in updated_response.json()[activity_name]["participants"]


def test_remove_nonexistent_participant_fails(client):
    """
    Test removal fails when participant not registered
    
    Arrange: Prepare an email not in the activity
    Act: Try to remove non-existent participant
    Assert: Response is 400 with error message
    """
    # Arrange
    activity_name = "Chess Club"
    nonexistent_email = "notregistered@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{nonexistent_email}"
    )
    
    # Assert
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_remove_from_nonexistent_activity_fails(client):
    """
    Test removal fails for non-existent activity
    
    Arrange: Prepare a non-existent activity name
    Act: Try to remove from non-existent activity
    Assert: Response is 404 with error message
    """
    # Arrange
    fake_activity = "Fake Activity That Does Not Exist"
    email = "test@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{fake_activity}/participants/{email}"
    )
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_participant_case_sensitive(client):
    """
    Test removal with different case for activity name
    
    Arrange: Use different case for activity name
    Act: DELETE with lowercase activity name
    Assert: Response is 404 (activity not found due to case sensitivity)
    """
    # Arrange
    activity_name = "chess club"  # lowercase
    email = "test@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )
    
    # Assert
    assert response.status_code == 404


def test_remove_participant_email_case_sensitive(client):
    """
    Test removal with different case for email
    
    Arrange: Get existing participant, try to remove with different case
    Act: DELETE with different case email
    Assert: Response is 400 (participant not found due to case sensitivity)
    """
    # Arrange
    activity_name = "Chess Club"
    initial_response = client.get("/activities")
    actual_email = initial_response.json()[activity_name]["participants"][0]
    different_case_email = actual_email.upper()
    
    # Only test if email actually changes with case conversion
    if different_case_email != actual_email:
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{different_case_email}"
        )
        
        # Assert
        assert response.status_code == 400


def test_remove_response_contains_message(client):
    """
    Test that removal response contains success message
    
    Arrange: Get existing participant
    Act: DELETE the participant
    Assert: Response body contains message field with expected format
    """
    # Arrange
    activity_name = "Programming Class"
    initial_response = client.get("/activities")
    participant = initial_response.json()[activity_name]["participants"][0]
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{participant}"
    )
    
    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert participant in response_data["message"]
    assert activity_name in response_data["message"]


def test_remove_multiple_participants_independently(client):
    """
    Test that removing one participant doesn't affect others
    
    Arrange: Get activity with multiple participants
    Act: Remove first participant, verify others remain
    Assert: Only removed participant is gone, others are still there
    """
    # Arrange
    activity_name = "Gym Class"  # Has multiple participants
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity_name]["participants"].copy()
    first_participant = initial_participants[0]
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{first_participant}"
    )
    
    # Assert
    assert response.status_code == 200
    
    # Verify state after removal
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    
    assert first_participant not in updated_participants
    
    # Verify other participants are still there
    for participant in initial_participants[1:]:
        assert participant in updated_participants
