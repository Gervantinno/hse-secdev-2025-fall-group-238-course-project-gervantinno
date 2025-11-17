# Recipe Manager API

Менеджер рецептов с ингредиентами и планированием питания (HSE SecDev 2025).

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу: **http://127.0.0.1:8000**

### Интерактивная документация (Swagger UI)

Открой в браузере: **http://127.0.0.1:8000/docs**

## Основные сущности

- User (аутентификация/авторизация)
- Recipe (название, шаги приготовления)
- Ingredient (название)
- RecipeIngredient (количество, единица измерения)
- MealPlan (календарь питания)

## API Endpoints

### Аутентификация

- `POST /auth/register` - регистрация пользователя
- `POST /auth/login` - вход в систему (JWT)

### Рецепты

- `GET /recipes` - список рецептов с пагинацией (limit/offset)
- `GET /recipes/{id}` - получение рецепта
- `POST /recipes` - создание рецепта (только авторизованные)
- `PUT /recipes/{id}` - обновление рецепта (только владелец)
- `DELETE /recipes/{id}` - удаление рецепта (только владелец)
- `GET /recipes?ingredient={name}` - фильтр по ингредиенту

### Ингредиенты

- `GET /ingredients` - список ингредиентов
- `POST /ingredients` - добавление ингредиента
- `PUT /ingredients/{id}` - обновление ингредиента
- `DELETE /ingredients/{id}` - удаление ингредиента

## Технологический стек

- Backend: Python/FastAPI
- Database: SQLite (dev) / PostgreSQL (prod)
- Testing: Pytest

## Ритуал перед PR

```bash
ruff check --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

## Тесты

```bash
pytest -q
```

## CI

В репозитории настроен workflow **CI** (GitHub Actions) — required check для `main`.
Badge добавится автоматически после загрузки шаблона в GitHub.

## Контейнеры

```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

## Эндпойнты

- `GET /health` → `{"status": "ok"}`
- `POST /items?name=...` — демо-сущность
- `GET /items/{id}`

## Формат ошибок

Все ошибки — JSON-обёртка:

```json
{
  "error": { "code": "not_found", "message": "item not found" }
}
```

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.
