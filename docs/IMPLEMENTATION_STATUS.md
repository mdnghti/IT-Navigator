# IT-Navigator - Профориентационная платформа

Полнофункциональная платформа для профориентационного тестирования с адаптивными тестами, системой подсчета баллов и административной панелью.

## 🚀 Технологический стек

### Backend
- **FastAPI** - современный веб-фреймворк
- **PostgreSQL** - основная база данных
- **SQLAlchemy 2.0** - ORM с async поддержкой
- **Alembic** - миграции БД
- **Redis** - кэширование и брокер сообщений
- **Celery** - фоновые задачи
- **SQLAdmin** - административная панель
- **JWT** - аутентификация

### Frontend
- **Next.js 14** - React фреймворк с App Router
- **TypeScript** - типизация
- **Tailwind CSS** - стилизация
- **Zustand** - управление состоянием
- **React Query** - работа с API

### Infrastructure
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - reverse proxy
- **GitHub Actions** - CI/CD
- **Flower** - мониторинг Celery

## 📋 Реализованные блоки

### ✅ Блок 1 - Фундамент
- [x] Структура проекта
- [x] Docker Compose с PostgreSQL
- [x] SQLAlchemy модели (User, Specialty, Test, Question, Answer, TestResult)
- [x] Alembic миграции
- [x] FastAPI с JWT авторизацией
- [x] SQLAdmin панель для конструктора тестов
- [x] Pre-commit hooks (Ruff, Mypy)

### ✅ Блок 2 - Ядро тестирования
- [x] Pydantic схемы для API
- [x] CRUD операции для тестов
- [x] Алгоритм подсчета баллов по специальностям
- [x] API эндпоинты:
  - GET `/api/v1/tests/general/questions` - получить вопросы общего теста
  - POST `/api/v1/tests/general/submit` - отправить ответы
  - GET `/api/v1/tests/specialized/{code}/questions` - вопросы специализированного теста
  - POST `/api/v1/tests/specialized/{code}/submit` - отправить ответы
  - GET `/api/v1/tests/results/my` - история результатов
  - GET `/api/v1/tests/results/{id}` - конкретный результат

### ✅ Блок 3 - Фронтенд
- [x] Next.js приложение с TypeScript
- [x] Страницы: login, register, dashboard, test, results
- [x] Компоненты для тестирования
- [x] API клиент с axios
- [x] Zustand store для состояния теста
- [x] Nginx конфигурация для роутинга

### ✅ Блок 4 - Фоновые задачи и аналитика
- [x] Redis в docker-compose
- [x] Celery worker с задачами:
  - `run_scoring` - подсчет результатов в фоне
  - `generate_pdf_report` - генерация PDF отчетов
- [x] Flower для мониторинга задач (порт 5555)
- [x] Redis кэширование вопросов (TTL 10 минут)
- [x] История результатов пользователя

### ✅ Блок 5 - Стабилизация и деплой
- [x] Pytest test suite:
  - `test_auth.py` - тесты авторизации (8 тестов)
  - `test_scoring.py` - тесты алгоритма подсчета (6 тестов)
  - `test_tests_api.py` - тесты API эндпоинтов (9 тестов)
- [x] GitHub Actions CI/CD для backend и frontend
- [x] Production docker-compose.prod.yml
- [x] Nginx production конфигурация с SSL
- [x] Логирование

## 🏃 Быстрый старт

### Требования
- Docker и Docker Compose
- Node.js 20+ (для локальной разработки frontend)
- Python 3.12+ (для локальной разработки backend)

### 1. Клонирование и настройка

```bash
cd IT-Navigator
```

### 2. Настройка переменных окружения

Создайте файл `backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://career_user:career_password@db:5432/career_platform
POSTGRES_USER=career_user
POSTGRES_PASSWORD=career_password
POSTGRES_DB=career_platform

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost"]

# App
DEBUG=true
PROJECT_NAME=Career Platform API
API_V1_PREFIX=/api/v1
```

### 3. Запуск всех сервисов

```bash
docker-compose up -d
```

Это запустит:
- **PostgreSQL** на порту 5432
- **Redis** (внутренний)
- **Backend API** на порту 8000
- **Celery Worker** (фоновые задачи)
- **Flower** на порту 5555 (мониторинг Celery)
- **Frontend** на порту 3000
- **Nginx** на порту 80 (роутинг всех сервисов)

### 4. Применение миграций

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Доступ к сервисам

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/v1
- **API Docs**: http://localhost/docs
- **Admin Panel**: http://localhost/admin
- **Flower**: http://localhost:5555

## 🧪 Запуск тестов

### Backend тесты

```bash
cd backend
pip install -e ".[dev]"
pytest --cov=app --cov-report=term
```

Или через Docker:

```bash
docker-compose exec backend pytest
```

### Линтинг и форматирование

```bash
cd backend
ruff check app
ruff format app
mypy app
```

## 📊 Структура проекта

```
IT-Navigator/
├── backend/
│   ├── app/
│   │   ├── admin/          # SQLAdmin views
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # config, security, cache, logging
│   │   ├── crud/           # database operations
│   │   ├── db/
│   │   │   ├── models/     # SQLAlchemy models
│   │   │   └── session.py
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── worker/         # Celery tasks
│   │   └── main.py
│   ├── alembic/            # database migrations
│   ├── tests/              # pytest tests
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js pages
│   │   ├── components/     # React components
│   │   ├── lib/            # API client
│   │   ├── store/          # Zustand stores
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── nginx/
│   ├── nginx.conf          # development config
│   └── nginx.prod.conf     # production config
├── .github/workflows/
│   └── ci.yml              # CI/CD pipeline
├── docker-compose.yml      # development
└── docker-compose.prod.yml # production
```

## 🔧 Разработка

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Celery Worker (локально)

```bash
cd backend
celery -A app.worker.celery_app worker -Q scoring,reports --loglevel=info
```

## 📝 API Endpoints

### Аутентификация
- `POST /api/v1/auth/register` - регистрация
- `POST /api/v1/auth/login` - вход
- `GET /api/v1/auth/me` - текущий пользователь

### Тесты
- `GET /api/v1/tests/general/questions` - вопросы общего теста
- `POST /api/v1/tests/general/submit` - отправить ответы
- `GET /api/v1/tests/specialized/{code}/questions` - специализированный тест
- `POST /api/v1/tests/specialized/{code}/submit` - отправить ответы
- `GET /api/v1/tests/results/my` - мои результаты
- `GET /api/v1/tests/results/{id}` - конкретный результат

## 🎯 Административная панель

Доступ: http://localhost/admin

Функции:
- Управление специальностями (F1-F7)
- Создание и редактирование тестов
- Конструктор вопросов
- Настройка весов ответов
- Управление пользователями

## 🚀 Production деплой

```bash
# Создайте .env.prod с production настройками
docker-compose -f docker-compose.prod.yml up -d

# Примените миграции
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## 📈 Мониторинг

- **Flower**: http://localhost:5555 - мониторинг Celery задач
- **Logs**: `docker-compose logs -f [service_name]`

## 🧪 Покрытие тестами

- ✅ Аутентификация (регистрация, логин, токены)
- ✅ Алгоритм подсчета баллов (100%, 0%, смешанные результаты)
- ✅ API эндпоинты (получение вопросов, отправка ответов, результаты)
- ✅ Авторизация и права доступа

## 📄 Лицензия

MIT

## 👥 Команда

Разработано для профориентационной платформы IT-Navigator
