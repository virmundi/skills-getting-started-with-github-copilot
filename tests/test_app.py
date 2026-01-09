import pytest
from fastapi import HTTPException

def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Should have activities

    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_success(client):
    """Test successful signup for an activity"""
    # Use an activity that exists
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Sign up with a new email
    new_email = "test@example.com"
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert new_email in data["message"]
    assert activity_name in data["message"]

def test_signup_activity_not_found(client):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/NonExistentActivity/signup",
        params={"email": "test@example.com"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up(client):
    """Test signup when already signed up"""
    # First get an existing participant
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]
    existing_email = activities[activity_name]["participants"][0]

    # Try to sign up again
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email}
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_unregister_success(client):
    """Test successful unregister from an activity"""
    # First sign up a test user
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    test_email = "unregister_test@example.com"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )

    # Now unregister
    response = client.delete(
        f"/activities/{activity_name}/participants/{test_email}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]
    assert activity_name in data["message"]

def test_unregister_activity_not_found(client):
    """Test unregister from non-existent activity"""
    response = client.delete(
        "/activities/NonExistentActivity/participants/test@example.com"
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_not_signed_up(client):
    """Test unregister when not signed up"""
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Try to unregister someone not signed up
    response = client.delete(
        f"/activities/{activity_name}/participants/notsignedup@example.com"
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]