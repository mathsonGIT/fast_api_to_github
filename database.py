import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text

DATABASE_URL = "sqlite+aiosqlite:///./main.py.db"

engine = create_async_engine(DATABASE_URL, echo=True)
# expire_on_commit=False will prevent attributes from being expired
# after commit.
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

session = async_session()


Base = declarative_base()


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    views = Column(Integer, default=0)
    cooking_time = Column(Integer)  # Время приготовления в минутах
    ingredients = Column(Text)  # Список ингредиентов
    description = Column(Text)  # Текстовое описание

    def __repr__(self):
        return f"<Recipe(title={self.title}, views={self.views}, cooking_time={self.cooking_time})>"


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_recipe(title, views, cooking_time, ingredients, description):
    async with async_session() as session:
        async with session.begin():
            new_recipe = Recipe(
                title=title,
                views=views,
                cooking_time=cooking_time,
                ingredients=ingredients,
                description=description,
            )
            session.add(new_recipe)


async def main():
    await init_db()
    await add_recipe(
        "Pasta",
        100,
        30,
        "Pasta, Tomato Sauce, Cheese",
        "Delicious pasta with tomato sauce.",
    )


if __name__ == "__main__":
    asyncio.run(main())
