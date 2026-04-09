"""Test suite for the Mergington High School API."""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirect_to_static_index_html(self, client):
        # Arrange
        expected_status_code = 307

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == expected_status_code
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the get activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activity_count = 9
        expected_activity_names = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Drama Club",
            "Art Studio",
            "Robotics Club",
            "Debate Team",
        ]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        for activity_name in expected_activity_names:
            assert activity_name in data

    def test_get_activities_activity_has_correct_fields(self, client):
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert (
                    field in activity_data
                ), f"Field '{field}' missing from activity '{activity_name}'"

    def test_get_activities_chess_club_has_initial_participants(self, client):
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]

        # Assert
        assert chess_club["participants"] == expected_participants


class TestSignupEndpoint:
    """Tests for the signup endpoint."""

    def test_signup_for_activity_success(self, client, sample_email):
        # Arrange
        activity_name = "Chess Club"
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {sample_email} for {activity_name}"
        }

        # Verify participant was added
        updated_count = len(client.get("/activities").json()[activity_name]["participants"])
        assert updated_count == initial_count + 1

    def test_signup_for_nonexistent_activity_returns_404(self, client, sample_email):
        # Arrange
        nonexistent_activity = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_participant_rejected(self, client):
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_different_activities(self, client, sample_email):
        # Arrange
        activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act & Assert
        for activity in activities:
            response = client.post(
                f"/activities/{activity}/signup?email={sample_email}"
            )
            assert response.status_code == 200
            assert activity in response.json()["message"]


class TestDeleteParticipantEndpoint:
    """Tests for the delete participant endpoint."""

    def test_delete_participant_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_count = len(client.get("/activities").json()[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Removed {email_to_remove} from {activity_name}"
        }

        # Verify participant was removed
        updated_count = len(client.get("/activities").json()[activity_name]["participants"])
        assert updated_count == initial_count - 1
        assert email_to_remove not in client.get("/activities").json()[activity_name]["participants"]

    def test_delete_participant_from_nonexistent_activity_returns_404(self, client):
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_delete_nonexistent_participant_returns_404(self, client):
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]