# Recipe Manager API

![CI](https://github.com/hse-secdev-2025-fall-group-238-course-project-gervantinno/hse-secdev-2025-fall-group-238-course-project-gervantinno/actions/workflows/ci.yml/badge.svg)

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

## Контейнеризация и харднинг (P07)

- **Базовый образ**: `python:3.12.7-slim` (multi-stage). На runtime-слое только runtime-зависимости, curl и приложение.
- **Безопасность**: non-root пользователь `app`, `no-new-privileges`, `cap_drop: [ALL]`, read-only root FS + tmpfs `/tmp`, отдельный volume `/data` для БД, healthcheck → `GET /health`.
- **Проверки**: CI прогоняет Hadolint, собирает образ, сканирует его Trivy (артефакт `trivy-report.txt`), убеждается, что `id -u != 0` внутри контейнера, и ждёт `healthy` от встроенного `HEALTHCHECK`.

### Локальный запуск образа

```bash
# собрать оптимизированный runtime-слой
docker build --target runtime -t recipe-manager:local .

# убедиться, что процесс не под root (должно вернуть число != 0)
docker run --rm --entrypoint /bin/sh recipe-manager:local -c "id -u"

# проверить healthcheck и API
docker run -d --name recipe-api -p 8000:8000 recipe-manager:local
docker inspect --format='{{.State.Health.Status}}' recipe-api
curl http://127.0.0.1:8000/health
docker rm -f recipe-api
```

### Docker Compose

```bash
cp .env.example .env
docker compose --env-file .env up --build
```

Compose поднимает сервис `api` с healthcheck, tempfs `/tmp`, volume `app-data:/data` (для SQLite или миграций) и пробрасывает `${APP_PORT:-8000}` наружу.

Доп. материалы: `docs/P07_container.md`.

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
