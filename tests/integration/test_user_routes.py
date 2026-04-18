from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)


def unique_user_data(prefix="user"):
    unique = uuid.uuid4().hex[:8]
    return {
        "username": f"{prefix}_{unique}",
        "email": f"{prefix}_{unique}@example.com",
        "password": "Password123"
    }


def test_register_user():
    user_data = unique_user_data("testuser")
    response = client.post("/users/register", json=user_data)

    assert response.status_code == 200, response.json()
    assert response.json()["username"] == user_data["username"]


def test_login_user():
    user_data = unique_user_data("loginuser")
    register_response = client.post("/users/register", json=user_data)
    assert register_response.status_code == 200, register_response.json()

    response = client.post("/users/login", json={
        "username": user_data["username"],
        "password": user_data["password"]
    })

    assert response.status_code == 200, response.json()
    assert response.json()["message"] == "Login successful"