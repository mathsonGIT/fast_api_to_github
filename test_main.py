import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_create_recipe():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/recipes",
            json={
                "title": "Test Recipe",
                "cooking_time": 30,
                "ingredients": "Test ingredients",
                "description": "Test description",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Recipe"
        assert data["cooking_time"] == 30
        assert data["ingredients"] == "Test ingredients"
        assert data["description"] == "Test description"
        assert data["views"] == 0
