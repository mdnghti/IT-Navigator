# Career Platform Backend

Профориентационная платформа - Backend API

## Технологии

- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy 2.0** - async ORM
- **PostgreSQL** - база данных
- **Alembic** - миграции БД
- **SQLAdmin** - админ-панель
- **JWT** - аутентификация
- **Docker** - контейнеризация

## Быстрый старт

### 1. Настройка окружения

```bash
# Скопировать .env.example в .env
cp .env.example .env

# Отредактировать .env и установить SECRET_KEY
```

### 2. Запуск через Docker Compose

```bash
# Из корневой директории проекта
docker-compose up -d

# Проверить логи
docker-compose logs -f backend
```

### 3. Применить миграции

```bash
# Войти в контейнер backend
docker-compose exec backend bash

# Создать миграцию
alembic revision --autogenerate -m "initial tables"

# Применить миграции
alembic upgrade head
```

### 4. Создать первого админа

```bash
# В контейнере backend запустить Python
docker-compose exec backend python

# В Python консоли:
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print("Admin created!")

asyncio.run(create_admin())
```

## API Endpoints

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Admin Panel**: http://localhost:8000/admin

### Авторизация

- `POST /api/v1/auth/register` - регистрация
- `POST /api/v1/auth/login` - вход (получение JWT токена)

## Структура проекта

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── auth.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── db/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── specialty.py
│   │   │   ├── test.py
│   │   │   ├── question.py
│   │   │   ├── answer.py
│   │   │   └── result.py
│   │   ├── base.py
│   │   └── session.py
│   ├── schemas/
│   │   ├── user.py
│   │   └── test.py
│   ├── crud/
│   │   ├── user.py
│   │   └── test.py
│   ├── admin/
│   │   ├── auth.py
│   │   └── views.py
│   └── main.py
├── alembic/
├── tests/
├── pyproject.toml
├── Dockerfile
└── .env
```

## Разработка

### Установка зависимостей локально

```bash
cd backend
pip install -e ".[dev]"
```

### Запуск тестов

```bash
pytest
pytest --cov=app --cov-report=html
```

### Линтинг и форматирование

```bash
ruff check .
ruff format .
mypy app
```

### Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Модели данных

### User
- Пользователи системы
- JWT аутентификация
- Роли: обычный пользователь / админ

### Specialty
- Специальности (F1-F7)
- Код, название, описание

### Test
- Тесты (общий / специализированный)
- Связь со специальностью

### Question
- Вопросы теста
- Связь с тестом и специальностью

### Answer
- Варианты ответов
- Вес для подсчёта баллов

### TestResult
- Результаты прохождения тестов
- JSON с ответами и баллами

## Админ-панель

Доступна по адресу: http://localhost:8000/admin

Функционал:
- Управление пользователями
- Создание специальностей
- Конструктор тестов
- Управление вопросами и ответами
- Назначение весов ответам

## Переменные окружения

```env
# Database
POSTGRES_USER=career_user
POSTGRES_PASSWORD=career_password
POSTGRES_DB=career_platform
DATABASE_URL=postgresql+asyncpg://career_user:career_password@db:5432/career_platform

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# App
DEBUG=true
```

## Лицензия

MIT
