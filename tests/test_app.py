import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Test client fixture for FastAPI app"""
    return TestClient(app)


class TestActivitiesAPI:
    """Test suite for Mergington High School Activities API"""

    def test_get_activities(self, client):
        """Test GET /activities returns all activities"""
        response = client.get("/activities")

        assert response.status_code == 200
        activities = response.json()

        # Verify we have activities
        assert isinstance(activities, dict)
        assert len(activities) > 0

        # Check structure of first activity
        first_activity = next(iter(activities.values()))
        required_keys = ["description", "schedule", "max_participants", "participants"]
        for key in required_keys:
            assert key in first_activity

        # Verify participants is a list
        assert isinstance(first_activity["participants"], list)

    def test_get_activities_specific_activity(self, client):
        """Test GET /activities returns correct data for a known activity"""
        response = client.get("/activities")
        activities = response.json()

        # Test with Chess Club (known from app.py)
        assert "Chess Club" in activities
        chess_club = activities["Chess Club"]

        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Gym Class"
    ])
    def test_signup_success(self, client, activity_name):
        """Test successful signup for various activities"""
        email = "test.student@mergington.edu"

        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert f"Signed up {email} for {activity_name}" in result["message"]

        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_email(self, client):
        """Test signup fails when email is already registered"""
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"

        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Second signup with same email
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup fails for non-existent activity"""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    @pytest.mark.parametrize("activity_name,email", [
        ("Chess Club", "michael@mergington.edu"),  # Already signed up
        ("Programming Class", "emma@mergington.edu"),  # Already signed up
    ])
    def test_unregister_success(self, client, activity_name, email):
        """Test successful unregistration from activities"""
        # Verify initially signed up
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

        # Unregister
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert f"Unregistered {email} from {activity_name}" in result["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test unregister fails when email is not registered"""
        activity_name = "Chess Club"
        email = "notsignedup@mergington.edu"

        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "not signed up" in result["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister fails for non-existent activity"""
        response = client.delete(
            "/activities/NonExistentActivity/signup",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_root_redirect(self, client):
        """Test root endpoint redirects to static HTML"""
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"