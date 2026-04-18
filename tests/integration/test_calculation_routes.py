from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)


def create_test_user():
    unique = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"calcuser_{unique}",
        "email": f"calcuser_{unique}@example.com",
        "password": "Password123"
    }

    response = client.post("/users/register", json=user_data)
    assert response.status_code == 200, response.json()
    return response.json()["id"]


def test_create_read_update_delete_calculation():
    user_id = create_test_user()

    create_response = client.post("/calculations/", json={
        "type": "addition",
        "inputs": [10, 5],
        "user_id": user_id
    })
    assert create_response.status_code == 200, create_response.json()
    calc_id = create_response.json()["id"]

    read_response = client.get(f"/calculations/{calc_id}")
    assert read_response.status_code == 200, read_response.json()
    assert read_response.json()["result"] == 15

    update_response = client.put(f"/calculations/{calc_id}", json={
        "inputs": [20, 5]
    })
    assert update_response.status_code == 200, update_response.json()
    assert update_response.json()["result"] == 25

    delete_response = client.delete(f"/calculations/{calc_id}")
    assert delete_response.status_code == 200, delete_response.json()