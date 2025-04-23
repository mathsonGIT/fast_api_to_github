import pytest_asyncio
import pytest
from database import engine, Base
from httpx import AsyncClient, ASGITransport
from main import app


@pytest_asyncio.fixture(scope="module")
async def test_client():
    # Create the database and tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create an AsyncClient instance for testing
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client  # Yield the client for use in tests

    # Teardown: drop the database tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_recipe(test_client):
    # Create a new recipe
    recipe_data = {
        "title": "Test Recipe",
        "cooking_time": 30,
        "ingredients": "Test Ingredient 1, Test Ingredient 2",
        "description": "This is a test recipe.",
    }

    response = await test_client.post("/recipes", json=recipe_data)
    assert response.status_code == 200
    assert response.json()["title"] == recipe_data["title"]
    assert "id" in response.json()
