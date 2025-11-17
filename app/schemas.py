from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field, constr


class UserBase(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class IngredientBase(BaseModel):
    name: constr(min_length=1, max_length=100)


class IngredientCreate(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    amount: float = Field(gt=0)
    unit: constr(min_length=1, max_length=20)


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeIngredient(RecipeIngredientBase):
    ingredient: Ingredient

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    title: constr(min_length=1, max_length=100)
    steps: constr(min_length=1, max_length=2000)


class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientCreate] = Field(
        max_length=30
    )  # NFR-13 requirement


class Recipe(RecipeBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    ingredients: List[RecipeIngredient]

    class Config:
        from_attributes = True


class RecipeList(BaseModel):
    items: List[Recipe]
    total: int
    offset: int
    limit: int
