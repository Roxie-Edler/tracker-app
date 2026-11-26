
import pytest # type: ignore

from tracker import create_app # type: ignore
from tracker.extensions import db # type: ignore


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    # Register a test user
    register_response = client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code == 201

    # Log in
    login_response = client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    # Return a client with authentication
    client.environ_base["HTTP_AUTHORIZATION"] = (
        f"Bearer {token}"
    )

    return client



def test_get_tasks_empty_collection(authenticated_client):
    response = authenticated_client.get("/auth/tasks")

    assert response.status_code == 200

    data = response.get_json()

    assert data["items"] == []
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 20
    assert data["pagination"]["total"] == 0
    assert data["pagination"]["pages"] == 0



def test_get_tasks_pagination(authenticated_client):
    # Create five tasks
    for i in range(1, 6):
        response = authenticated_client.post(
            "/auth/tasks",
            json={"title": f"Task {i}"}
        )
        assert response.status_code == 201

    # Request page 1
    response = authenticated_client.get(
        "/auth/tasks?page=1&per_page=2"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["items"]) == 2
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 2
    assert data["pagination"]["total"] == 5
    assert data["pagination"]["pages"] == 3

    # Request final page
    response = authenticated_client.get(
        "/auth/tasks?page=3&per_page=2"
    )

    data = response.get_json()

    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Task 5"

    # Request beyond final page
    response = authenticated_client.get(
        "/auth/tasks?page=4&per_page=2"
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["items"] == []
    assert data["pagination"]["pages"] == 3



def test_get_tasks_invalid_pagination(authenticated_client):
    # per_page cannot be zero
    response = authenticated_client.get(
        "/auth/tasks?page=1&per_page=0"
    )

    assert response.status_code == 400
    assert response.get_json()["code"] == "validation_error"

    # per_page cannot exceed 100
    response = authenticated_client.get(
        "/auth/tasks?page=1&per_page=101"
    )

    assert response.status_code == 400

    # page must be positive
    response = authenticated_client.get(
        "/auth/tasks?page=0&per_page=2"
    )

    assert response.status_code == 400

    # page must be an integer
    response = authenticated_client.get(
        "/auth/tasks?page=abc&per_page=2"
    )

    assert response.status_code == 400


