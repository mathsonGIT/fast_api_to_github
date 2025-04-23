from fastapi.testclient import TestClient

from main import app


def test_create_recipe():
    client = TestClient(app)
    response = client.get("/recipes")
    assert response.status_code == 200
