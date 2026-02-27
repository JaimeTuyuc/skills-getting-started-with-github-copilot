import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity database before each test."""
    original = copy.deepcopy(activities)
    yield
    # restore by mutating the dict in place (app also references this variable)
    activities.clear()
    activities.update(original)


def test_root_redirect():
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"

    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_signed_up():
    # Arrange
    email = "michael@mergington.edu"  # already in the initial list

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_success():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete("/activities/Nonexistent/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up():
    # Arrange
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
