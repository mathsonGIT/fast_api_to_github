from fastapi import FastAPI, HTTPException
from database import engine, session
from models import Recipe, Base
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy import insert


class RecipeCreate(BaseModel):
    title: str
    cooking_time: int
    ingredients: str
    description: str


class RecipeResponse(BaseModel):
    id: int
    title: str
    views: int
    cooking_time: int
    ingredients: str
    description: str

    class Config:
        orm_mode = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await session.close()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


@app.get("/recipes", response_model=List[RecipeResponse])
async def get_recipes(limit: int = 10):
    """
    Получить список всех рецептов, отсортированных по количеству просмотров и времени приготовления.
    """
    query = select(Recipe).order_by(Recipe.views.desc(), Recipe.cooking_time).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int):
    """
    Получить детальную информацию о конкретном рецепте по его ID.
    """
    query = select(Recipe).where(Recipe.id == recipe_id)
    result = await session.execute(query)
    recipe = result.scalars().one_or_none()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.post("/recipes", response_model=RecipeResponse)
async def create_recipe(recipe: RecipeCreate):
    """
    Создать новый рецепт.
    """
    query = insert(Recipe).values(**recipe.dict())
    result = await session.execute(query)
    await session.commit()
    recipe_id = result.inserted_primary_key[0]
    return {**recipe.dict(), "id": recipe_id, "views": 0}
