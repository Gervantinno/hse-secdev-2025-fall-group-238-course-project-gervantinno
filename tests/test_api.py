import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# Positive tests
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_user_success(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "id" in data


def test_login_success(client):
    # Register first
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )

    # Login
    response = client.post(
        "/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_create_ingredient(client):
    response = client.post("/ingredients", json={"name": "Salt"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Salt"
    assert "id" in data


def test_list_ingredients(client):
    # Create ingredient
    client.post("/ingredients", json={"name": "Salt"})
    client.post("/ingredients", json={"name": "Pepper"})

    # List
    response = client.get("/ingredients")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_create_recipe_with_auth(client):
    # Register and login
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    login_response = client.post(
        "/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create ingredient
    ing_response = client.post("/ingredients", json={"name": "Salt"})
    ingredient_id = ing_response.json()["id"]

    # Create recipe
    response = client.post(
        "/recipes",
        headers=headers,
        json={
            "title": "Simple Recipe",
            "steps": "1. Add salt\n2. Mix",
            "ingredients": [
                {"ingredient_id": ingredient_id, "amount": 1.0, "unit": "tsp"}
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Simple Recipe"
    assert len(data["ingredients"]) == 1


def test_list_recipes_with_pagination(client):
    response = client.get("/recipes?offset=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "offset" in data
    assert "limit" in data


# Negative tests
def test_register_duplicate_username(client):
    # Register first user
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "testpass123",
        },
    )

    # Try to register with same username
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )

    response = client.post(
        "/auth/login", json={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login", json={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401


def test_create_recipe_without_auth(client):
    response = client.post(
        "/recipes", json={"title": "Recipe", "steps": "Steps", "ingredients": []}
    )
    # Without auth should return 401 (not authenticated) or 403 (forbidden)
    assert response.status_code in (401, 403)


def test_get_nonexistent_recipe(client):
    response = client.get("/recipes/999")
    assert response.status_code == 404


def test_update_recipe_not_owner(client):
    # Create two users
    client.post(
        "/auth/register",
        json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "pass123456",  # Минимум 8 символов
        },
    )
    client.post(
        "/auth/register",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "pass123456",  # Минимум 8 символов
        },
    )

    # User1 creates recipe
    login1 = client.post(
        "/auth/login", json={"username": "user1", "password": "pass123456"}
    )
    token1 = login1.json()["access_token"]

    recipe_response = client.post(
        "/recipes",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "User1 Recipe", "steps": "Steps", "ingredients": []},
    )
    recipe_id = recipe_response.json()["id"]

    # User2 tries to update user1's recipe
    login2 = client.post(
        "/auth/login", json={"username": "user2", "password": "pass123456"}
    )
    token2 = login2.json()["access_token"]

    response = client.put(
        f"/recipes/{recipe_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"title": "Updated", "steps": "Updated steps", "ingredients": []},
    )
    assert response.status_code == 403


def test_delete_recipe_not_owner(client):
    # Create two users
    client.post(
        "/auth/register",
        json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "pass123456",  # Минимум 8 символов
        },
    )
    client.post(
        "/auth/register",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "pass123456",  # Минимум 8 символов
        },
    )

    # User1 creates recipe
    login1 = client.post(
        "/auth/login", json={"username": "user1", "password": "pass123456"}
    )
    token1 = login1.json()["access_token"]

    recipe_response = client.post(
        "/recipes",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "User1 Recipe", "steps": "Steps", "ingredients": []},
    )
    recipe_id = recipe_response.json()["id"]

    # User2 tries to delete user1's recipe
    login2 = client.post(
        "/auth/login", json={"username": "user2", "password": "pass123456"}
    )
    token2 = login2.json()["access_token"]

    response = client.delete(
        f"/recipes/{recipe_id}", headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 403


def test_invalid_token(client):
    response = client.get("/recipes", headers={"Authorization": "Bearer invalid_token"})
    # This should still work as /recipes doesn't require auth
    assert response.status_code == 200


def test_create_ingredient_duplicate_name(client):
    client.post("/ingredients", json={"name": "Salt"})

    response = client.post("/ingredients", json={"name": "Salt"})
    assert response.status_code == 400
