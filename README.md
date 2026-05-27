# IT Navigator - Career Guidance Platform

[Українська версія](#ukrainian-version) | [English version](#english-version)

---

<a name="english-version"></a>
## 🇬🇧 English Version

Full-stack career guidance platform with adaptive testing, detailed analytics, and multi-dimensional scoring system for IT specialties.

### 🚀 Features

- **Adaptive Testing**: General aptitude test + 7 specialized IT career tests
- **Multi-dimensional Scoring**: Weighted scoring across multiple specialty dimensions
- **User Management**: JWT authentication with secure password hashing
- **Admin Panel**: SQLAdmin interface for content management
- **Modern Frontend**: Next.js 14 with TypeScript, TanStack Query, and Zustand
- **Background Tasks**: Celery for async processing (scoring, PDF generation)
- **Responsive Design**: Dark-themed UI with Framer Motion animations

### 🏗️ Architecture

**Backend:**
- FastAPI + PostgreSQL 16 + SQLAlchemy (async)
- Celery + Redis for background tasks
- JWT authentication
- SQLAdmin panel
- Alembic migrations

**Frontend:**
- Next.js 14 + TypeScript
- TanStack Query (React Query)
- Zustand state management
- Tailwind CSS
- Framer Motion

**Infrastructure:**
- Docker Compose
- Nginx reverse proxy
- PostgreSQL + Redis

### 📦 Quick Start

#### 1. Prerequisites

- Docker & Docker Compose
- Git

#### 2. Clone & Setup

```bash
git clone https://github.com/mdnghti/IT-Navigator.git
cd IT-Navigator

# Create backend .env file
cp backend/.env.example backend/.env

# Generate SECRET_KEY and update backend/.env
openssl rand -hex 32

# Create frontend .env file
cp frontend/.env.example frontend/.env.local
```

#### 3. Launch Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

#### 4. Initialize Database

```bash
# Create admin user, specialties, and test data
docker-compose exec backend python -m scripts.init_db

# This creates:
# - Admin user (admin@example.com / admin123)
# - 7 IT specialties (F1-F7)
# - General test (13 questions)
# - 7 specialized tests (10 questions each)
```

#### 5. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin
  - Email: `admin@example.com`
  - Password: `admin123`

### 🔌 API Endpoints

#### Authentication

```bash
# Register
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}

# Login (get JWT token)
POST /api/v1/auth/login
username=user@example.com&password=password123
```

#### Testing

```bash
# Get general test questions (shuffled)
GET /api/v1/tests/general/questions
Authorization: Bearer <token>

# Submit general test answers
POST /api/v1/tests/general/submit
{
  "answers": [
    {"question_id": 1, "answer_id": 3}
  ]
}

# Get specialized test questions
GET /api/v1/tests/specialized/{specialty_code}/questions

# Get user's test history
GET /api/v1/tests/results/my

# Get specific test result
GET /api/v1/tests/results/{result_id}
```

### 🗂️ Project Structure

```
IT-Navigator/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API routes
│   │   ├── core/                # Config, security, logging
│   │   ├── crud/                # Database operations
│   │   ├── db/models/           # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── admin/               # SQLAdmin panel
│   │   └── worker/              # Celery tasks
│   ├── alembic/                 # Database migrations
│   ├── scripts/                 # Utility scripts
│   └── tests/                   # Pytest tests
├── frontend/
│   └── src/
│       ├── app/                 # Next.js App Router
│       ├── components/          # React components
│       ├── lib/                 # API client
│       ├── store/               # Zustand stores
│       └── types/               # TypeScript types
├── docker-compose.yml           # Development setup
└── docker-compose.prod.yml      # Production setup
```

### 🧪 Development

```bash
# Backend tests
cd backend
pytest
pytest --cov=app --cov-report=html

# Backend linting
ruff check .
ruff format .
mypy app

# Frontend development
cd frontend
npm run dev

# Frontend linting
npm run lint
```

### 🚢 Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment guide.

Quick version:
```bash
# 1. Configure .env files for production
# 2. Launch services
docker compose -f docker-compose.prod.yml up -d

# 3. Initialize database
docker compose exec backend python -m scripts.init_db
```

### 📊 Database Models

- **User**: Authentication and profile data
- **Specialty**: IT career specialties (F1-F7)
- **Test**: General and specialized tests
- **Question**: Test questions with shuffling
- **Answer**: Answer options with multi-dimensional weights
- **TestResult**: User test results with JSON scores

### 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy (async) |
| Task Queue | Celery + Redis |
| Authentication | JWT |
| Admin Panel | SQLAdmin |
| Frontend Framework | Next.js 14 |
| State Management | Zustand + TanStack Query |
| Styling | Tailwind CSS |
| Animations | Framer Motion |
| Containerization | Docker + Docker Compose |
| Reverse Proxy | Nginx |

### 📝 License

MIT

---

<a name="ukrainian-version"></a>
## 🇺🇦 Українська версія

Повнофункціональна платформа для профорієнтаційного тестування з адаптивними тестами, детальною аналітикою та багатовимірною системою оцінювання для IT-спеціальностей.

### 🚀 Можливості

- **Адаптивне тестування**: Загальний тест здібностей + 7 спеціалізованих IT-тестів
- **Багатовимірне оцінювання**: Зважена система балів за кількома вимірами спеціальностей
- **Управління користувачами**: JWT-автентифікація з безпечним хешуванням паролів
- **Адмін-панель**: SQLAdmin інтерфейс для управління контентом
- **Сучасний фронтенд**: Next.js 14 з TypeScript, TanStack Query та Zustand
- **Фонові завдання**: Celery для асинхронної обробки (підрахунок балів, генерація PDF)
- **Адаптивний дизайн**: Темна тема з анімаціями Framer Motion

### 🏗️ Архітектура

**Backend:**
- FastAPI + PostgreSQL 16 + SQLAlchemy (async)
- Celery + Redis для фонових завдань
- JWT автентифікація
- SQLAdmin панель
- Alembic міграції

**Frontend:**
- Next.js 14 + TypeScript
- TanStack Query (React Query)
- Zustand для стану
- Tailwind CSS
- Framer Motion

**Інфраструктура:**
- Docker Compose
- Nginx reverse proxy
- PostgreSQL + Redis

### 📦 Швидкий старт

#### 1. Вимоги

- Docker & Docker Compose
- Git

#### 2. Клонування та налаштування

```bash
git clone https://github.com/mdnghti/IT-Navigator.git
cd IT-Navigator

# Створити .env файл для backend
cp backend/.env.example backend/.env

# Згенерувати SECRET_KEY та оновити backend/.env
openssl rand -hex 32

# Створити .env файл для frontend
cp frontend/.env.example frontend/.env.local
```

#### 3. Запуск сервісів

```bash
# Запустити всі сервіси
docker-compose up -d

# Перевірити статус
docker-compose ps

# Переглянути логи
docker-compose logs -f backend
```

#### 4. Ініціалізація бази даних

```bash
# Створити адміна, спеціальності та тестові дані
docker-compose exec backend python -m scripts.init_db

# Це створить:
# - Адмін користувача (admin@example.com / admin123)
# - 7 IT-спеціальностей (F1-F7)
# - Загальний тест (13 питань)
# - 7 спеціалізованих тестів (по 10 питань кожен)
```

#### 5. Доступ до додатку

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Адмін-панель**: http://localhost:8000/admin
  - Email: `admin@example.com`
  - Пароль: `admin123`

### 🔌 API Endpoints

#### Автентифікація

```bash
# Реєстрація
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "Іван Петренко"
}

# Вхід (отримання JWT токена)
POST /api/v1/auth/login
username=user@example.com&password=password123
```

#### Тестування

```bash
# Отримати питання загального тесту (перемішані)
GET /api/v1/tests/general/questions
Authorization: Bearer <token>

# Відправити відповіді загального тесту
POST /api/v1/tests/general/submit
{
  "answers": [
    {"question_id": 1, "answer_id": 3}
  ]
}

# Отримати питання спеціалізованого тесту
GET /api/v1/tests/specialized/{specialty_code}/questions

# Отримати історію тестів користувача
GET /api/v1/tests/results/my

# Отримати конкретний результат тесту
GET /api/v1/tests/results/{result_id}
```

### 🗂️ Структура проєкту

```
IT-Navigator/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API маршрути
│   │   ├── core/                # Конфігурація, безпека, логування
│   │   ├── crud/                # Операції з БД
│   │   ├── db/models/           # SQLAlchemy моделі
│   │   ├── schemas/             # Pydantic схеми
│   │   ├── admin/               # SQLAdmin панель
│   │   └── worker/              # Celery завдання
│   ├── alembic/                 # Міграції БД
│   ├── scripts/                 # Утилітні скрипти
│   └── tests/                   # Pytest тести
├── frontend/
│   └── src/
│       ├── app/                 # Next.js App Router
│       ├── components/          # React компоненти
│       ├── lib/                 # API клієнт
│       ├── store/               # Zustand сховища
│       └── types/               # TypeScript типи
├── docker-compose.yml           # Development налаштування
└── docker-compose.prod.yml      # Production налаштування
```

### 🧪 Розробка

```bash
# Backend тести
cd backend
pytest
pytest --cov=app --cov-report=html

# Backend лінтинг
ruff check .
ruff format .
mypy app

# Frontend розробка
cd frontend
npm run dev

# Frontend лінтинг
npm run lint
```

### 🚢 Production деплой

Дивіться [DEPLOYMENT.md](DEPLOYMENT.md) для детальної інструкції з production деплою.

Коротка версія:
```bash
# 1. Налаштувати .env файли для production
# 2. Запустити сервіси
docker compose -f docker-compose.prod.yml up -d

# 3. Ініціалізувати базу даних
docker compose exec backend python -m scripts.init_db
```

### 📊 Моделі бази даних

- **User**: Дані автентифікації та профілю
- **Specialty**: IT-спеціальності (F1-F7)
- **Test**: Загальні та спеціалізовані тести
- **Question**: Питання тестів з перемішуванням
- **Answer**: Варіанти відповідей з багатовимірними вагами
- **TestResult**: Результати тестів користувачів з JSON балами

### 🛠️ Технологічний стек

| Компонент | Технологія |
|-----------|-----------|
| Backend Framework | FastAPI |
| База даних | PostgreSQL 16 |
| ORM | SQLAlchemy (async) |
| Черга завдань | Celery + Redis |
| Автентифікація | JWT |
| Адмін-панель | SQLAdmin |
| Frontend Framework | Next.js 14 |
| Управління станом | Zustand + TanStack Query |
| Стилізація | Tailwind CSS |
| Анімації | Framer Motion |
| Контейнеризація | Docker + Docker Compose |
| Reverse Proxy | Nginx |

### 📝 Ліцензія

MIT
