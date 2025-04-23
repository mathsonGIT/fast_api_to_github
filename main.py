from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database import Base, Recipe, engine

# Create a new sessionmaker for each request
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


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
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.get("/recipes", response_model=List[RecipeResponse])
async def get_recipes(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Получить список всех рецептов, отсортированных по количеству просмотров и времени приготовления.
    """
    query = (
        select(Recipe).order_by(Recipe.views.desc(), Recipe.cooking_time).limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить детальную информацию о конкретном рецепте по его ID.
    """
    query = select(Recipe).where(Recipe.id == recipe_id)
    result = await db.execute(query)
    recipe = result.scalars().one_or_none()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.post("/recipes", response_model=RecipeResponse)
async def create_recipe(recipe: RecipeCreate, db: AsyncSession = Depends(get_db)):
    """
    Создать новый рецепт.
    """
    query = insert(Recipe).values(**recipe.dict())
    result = await db.execute(query)
    await db.commit()
    recipe_id = result.inserted_primary_key[0]
    return RecipeResponse(**{**recipe.dict(), "id": recipe_id, "views": 0})
