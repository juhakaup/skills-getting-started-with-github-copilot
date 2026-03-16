import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state between tests."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_activities_contains_known_activity(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]


def test_signup_adds_participant(client):
    email = "test.student@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    activities_response = client.get("/activities").json()
    assert email in activities_response["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    email = "test.student@mergington.edu"

    first = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert first.status_code == 200

    second = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert second.status_code == 400

    activities_response = client.get("/activities").json()
    assert activities_response["Chess Club"]["participants"].count(email) == 1


def test_remove_participant(client):
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    activities_response = client.get("/activities").json()
    assert email not in activities_response["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404(client):
    email = "doesnotexist@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 404
