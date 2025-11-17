from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    recipes: Mapped[List["Recipe"]] = relationship("Recipe", back_populates="owner")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    steps: Mapped[str] = mapped_column(String(2000))
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    owner: Mapped[User] = relationship("User", back_populates="recipes")
    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="recipe"
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    recipes: Mapped[List["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="ingredient"
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id"), primary_key=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ingredients.id"), primary_key=True
    )
    amount: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))

    recipe: Mapped[Recipe] = relationship("Recipe", back_populates="ingredients")
    ingredient: Mapped[Ingredient] = relationship(
        "Ingredient", back_populates="recipes"
    )
