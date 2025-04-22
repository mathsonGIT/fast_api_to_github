from sqlalchemy import Column, Integer, String, Text
from database import Base

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