import pytest
from copy import deepcopy
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: make a deep copy of the activities dict before each test and
    restore it afterwards so tests don't interfere with one another.
    """
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture

def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


def test_root_redirect(client):
    # Arrange: client fixture is ready

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities(client):
    # Arrange: expected data is the current activities copy
    expected = deepcopy(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_success(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json().get("message", "")
    assert new_email in activities[activity_name]["participants"]


def test_signup_already_signed(client):
    # Arrange: pick an existing participant
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json().get("detail", "")


def test_signup_nonexistent(client):
    # Arrange
    activity_name = "Nonexistent"
    email = "someone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json().get("detail", "")


def test_signup_missing_email(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422  # validation error
    assert response.json()["detail"]
