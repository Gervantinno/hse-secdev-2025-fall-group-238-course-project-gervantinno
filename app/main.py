import logging
from datetime import timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user_from_token,
    get_password_hash,
    is_admin,
    verify_password,
)
from app.core.error_handler import rfc7807_exception_handler
from app.database import engine, get_db

logger = logging.getLogger(__name__)

# Create database tables
try:
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

app = FastAPI(
    title="Recipe Manager API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
    swagger_ui_init_oauth={},
)


# Configure OpenAPI schema for Bearer token
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title="Recipe Manager API",
        version="1.0.0",
        routes=app.routes,
    )

    # Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer token for authentication",
        }
    }

    # Mark protected endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method != "parameters":
                # Add security to all endpoints except:
                # /health, /auth/register, /auth/login, /ingredients GET
                if not any(
                    path.startswith(x)
                    for x in ["/health", "/openapi", "/docs", "/redoc"]
                ):
                    if path == "/ingredients" and method == "get":
                        continue
                    if path.startswith("/auth/"):
                        continue
                    if "security" not in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["security"] = [
                            {"bearer": []}
                        ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Add RFC7807 error handler
app.add_exception_handler(Exception, rfc7807_exception_handler)


# Helper to get current user
async def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> models.User:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split(" ")[1]
    username = get_current_user_from_token(token)
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.get("/health")
def health():
    return {"status": "ok"}


# Authentication endpoints
@app.post("/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = (
            db.query(models.User).filter(models.User.username == user.username).first()
        )
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            username=user.username, email=user.email, hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Error registering user")


@app.post("/auth/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.username == credentials.username)
        .first()
    )
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Recipe endpoints
@app.get("/recipes", response_model=schemas.RecipeList)
def list_recipes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    ingredient: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Recipe)

    if ingredient:
        query = (
            query.join(models.RecipeIngredient)
            .join(models.Ingredient)
            .filter(models.Ingredient.name.ilike(f"%{ingredient}%"))
        )

    total = query.count()
    recipes = query.offset(offset).limit(limit).all()

    return {"items": recipes, "total": total, "offset": offset, "limit": limit}


@app.post("/recipes", response_model=schemas.Recipe)
def create_recipe(
    recipe: schemas.RecipeCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if len(recipe.ingredients) > 30:  # NFR-13
        raise HTTPException(
            status_code=400, detail="Recipe cannot have more than 30 ingredients"
        )

    db_recipe = models.Recipe(
        title=recipe.title, steps=recipe.steps, owner_id=current_user.id
    )
    db.add(db_recipe)
    db.commit()

    # Add ingredients
    for ingredient_data in recipe.ingredients:
        db_ingredient = db.query(models.Ingredient).get(ingredient_data.ingredient_id)
        if not db_ingredient:
            raise HTTPException(
                status_code=404,
                detail=f"Ingredient {ingredient_data.ingredient_id} not found",
            )

        recipe_ingredient = models.RecipeIngredient(
            recipe_id=db_recipe.id,
            ingredient_id=ingredient_data.ingredient_id,
            amount=ingredient_data.amount,
            unit=ingredient_data.unit,
        )
        db.add(recipe_ingredient)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@app.get("/recipes/{recipe_id}", response_model=schemas.Recipe)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).get(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.put("/recipes/{recipe_id}", response_model=schemas.Recipe)
def update_recipe(
    recipe_id: int,
    recipe_update: schemas.RecipeCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_recipe = db.query(models.Recipe).get(recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Check ownership
    if db_recipe.owner_id != current_user.id and not is_admin(current_user):
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this recipe"
        )

    # Update recipe
    db_recipe.title = recipe_update.title
    db_recipe.steps = recipe_update.steps

    # Update ingredients
    db.query(models.RecipeIngredient).filter(
        models.RecipeIngredient.recipe_id == recipe_id
    ).delete()

    for ingredient_data in recipe_update.ingredients:
        recipe_ingredient = models.RecipeIngredient(
            recipe_id=recipe_id,
            ingredient_id=ingredient_data.ingredient_id,
            amount=ingredient_data.amount,
            unit=ingredient_data.unit,
        )
        db.add(recipe_ingredient)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@app.delete("/recipes/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_recipe = db.query(models.Recipe).get(recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Check ownership
    if db_recipe.owner_id != current_user.id and not is_admin(current_user):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this recipe"
        )

    db.delete(db_recipe)
    db.commit()
    return {"status": "ok"}


# Ingredient endpoints
@app.post("/ingredients", response_model=schemas.Ingredient)
def create_ingredient(
    ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)
):
    db_ingredient = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.name.ilike(ingredient.name))
        .first()
    )
    if db_ingredient:
        raise HTTPException(status_code=400, detail="Ingredient already exists")

    db_ingredient = models.Ingredient(name=ingredient.name)
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


@app.get("/ingredients", response_model=List[schemas.Ingredient])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(models.Ingredient).all()


@app.get("/ingredients/{ingredient_id}", response_model=schemas.Ingredient)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = db.query(models.Ingredient).get(ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@app.put("/ingredients/{ingredient_id}", response_model=schemas.Ingredient)
def update_ingredient(
    ingredient_id: int,
    ingredient_update: schemas.IngredientCreate,
    db: Session = Depends(get_db),
):
    db_ingredient = db.query(models.Ingredient).get(ingredient_id)
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Check if name is already used by another ingredient
    existing = (
        db.query(models.Ingredient)
        .filter(
            models.Ingredient.name.ilike(ingredient_update.name),
            models.Ingredient.id != ingredient_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Ingredient name already exists")

    db_ingredient.name = ingredient_update.name
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


@app.delete("/ingredients/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    db_ingredient = db.query(models.Ingredient).get(ingredient_id)
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    db.delete(db_ingredient)
    db.commit()
    return {"status": "ok"}
