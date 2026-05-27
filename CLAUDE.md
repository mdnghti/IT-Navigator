# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IT Navigator (Career Platform) is a full-stack career guidance platform with adaptive testing and detailed analytics. The system consists of:

- **Backend**: FastAPI + PostgreSQL + SQLAlchemy (async) + Celery
- **Frontend**: Next.js 14 + TypeScript + TanStack Query + Zustand
- **Infrastructure**: Docker Compose with PostgreSQL, Redis, Nginx

## Architecture

### Backend Structure (`backend/app/`)

```
app/
├── api/v1/endpoints/     # API route handlers
│   ├── auth.py          # JWT authentication endpoints
│   └── tests.py         # Test/question/result endpoints
├── core/                # Core configuration
│   ├── config.py        # Pydantic settings (env vars)
│   ├── security.py      # JWT & password hashing
│   └── logging.py       # Logging setup
├── db/
│   ├── models/          # SQLAlchemy models
│   │   ├── user.py      # User model with JWT auth
│   │   ├── specialty.py # Specialties (F1-F7)
│   │   ├── test.py      # Tests (general/specialized)
│   │   ├── question.py  # Test questions
│   │   ├── answer.py    # Answer options with weights
│   │   └── result.py    # TestResult with JSON scores
│   ├── base.py          # SQLAlchemy Base
│   └── session.py       # Async session factory
├── crud/                # Database operations
│   ├── test.py          # Test/question queries
│   └── scoring.py       # Score calculation logic
├── schemas/             # Pydantic schemas for API
├── admin/               # SQLAdmin panel
│   ├── auth.py          # Admin authentication
│   └── views.py         # Admin model views
├── worker/              # Celery tasks
│   ├── celery_app.py    # Celery configuration
│   └── tasks.py         # Background tasks (scoring, PDF)
└── main.py              # FastAPI app factory
```

### Frontend Structure (`frontend/src/`)

```
src/
├── app/                 # Next.js App Router
│   ├── (auth)/         # Auth route group
│   │   ├── login/
│   │   └── register/
│   ├── test/           # Testing pages
│   │   ├── general/
│   │   └── specialized/[code]/
│   ├── results/[id]/   # Test results
│   ├── dashboard/      # User dashboard
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Landing page
│   └── providers.tsx   # React Query provider
├── components/         # React components
│   ├── test/          # Test UI components
│   ├── results/       # Results display
│   └── ui/            # Reusable UI components
├── lib/
│   └── api.ts         # Axios client with JWT interceptor
├── store/
│   └── testStore.ts   # Zustand state management
└── types/
    └── index.ts       # TypeScript type definitions
```

### Key Architectural Patterns

1. **Async SQLAlchemy**: All database operations use `AsyncSession` and `async/await`
2. **JWT Authentication**: Token-based auth with `get_current_user` dependency
3. **Test Shuffling**: Questions and answers are randomized on fetch to prevent memorization
4. **Score Calculation**: Weighted scoring system maps answers to specialty scores
5. **Background Tasks**: Celery handles async scoring and PDF generation via Redis
6. **Admin Panel**: SQLAdmin provides CRUD interface for all models

## Development Commands

### Backend

```bash
# Start all services (from project root)
docker-compose up -d

# View backend logs
docker-compose logs -f backend

# Access backend container
docker-compose exec backend bash

# Run database migrations
docker-compose exec backend alembic revision --autogenerate -m "description"
docker-compose exec backend alembic upgrade head

# Initialize database with test data
docker-compose exec backend python scripts/init_db.py

# Run tests
cd backend
pytest
pytest --cov=app --cov-report=html

# Linting and formatting
cd backend
ruff check .
ruff format .
mypy app

# Install dependencies locally (for IDE support)
cd backend
pip install -e ".[dev]"
```

### Frontend

```bash
# Development mode
cd frontend
npm run dev

# Production build
cd frontend
npm run build
npm start

# Linting
cd frontend
npm run lint
```

### Celery

```bash
# View Celery worker logs
docker-compose logs -f celery_worker

# Access Flower monitoring UI
# http://localhost:5555
```

## Database Models & Relationships

- **User** → has many **TestResult**
- **Specialty** (F1-F7) → has many **Test** and **Question**
- **Test** (general/specialized) → has many **Question** → has many **Answer**
- **TestResult** stores JSON with `{specialty_code: score}` mapping

## API Endpoints

All API endpoints are prefixed with `/api/v1`:

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - Login (returns JWT token)

### Tests
- `GET /tests/general/questions` - Get shuffled general test questions
- `POST /tests/general/submit` - Submit general test answers
- `GET /tests/specialized/{code}/questions` - Get specialized test questions
- `POST /tests/specialized/{code}/submit` - Submit specialized test
- `GET /tests/results/my` - Get current user's test history
- `GET /tests/results/{id}` - Get specific test result

### Admin Panel
- `/admin` - SQLAdmin interface (requires admin user)
- `/docs` - Swagger API documentation
- `/health` - Health check endpoint

## Environment Variables

Backend requires `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://career_user:career_password@db:5432/career_platform
POSTGRES_USER=career_user
POSTGRES_PASSWORD=career_password
POSTGRES_DB=career_platform

# Security
SECRET_KEY=<generate with: openssl rand -hex 32>
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# App
DEBUG=true
```

Frontend requires `.env.local` in `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Testing Strategy

- Backend uses `pytest` with `pytest-asyncio` for async tests
- Test database fixtures should use `AsyncSession`
- Frontend testing not yet implemented

## Common Workflows

### Adding a New API Endpoint

1. Create/update endpoint in `backend/app/api/v1/endpoints/`
2. Add Pydantic schemas in `backend/app/schemas/`
3. Implement CRUD operations in `backend/app/crud/`
4. Update router in `backend/app/api/v1/router.py` if new file
5. Test with `/docs` Swagger UI

### Adding a New Database Model

1. Create model in `backend/app/db/models/`
2. Import in `backend/app/db/base.py`
3. Generate migration: `alembic revision --autogenerate -m "add model"`
4. Review and apply: `alembic upgrade head`
5. Add SQLAdmin view in `backend/app/admin/views.py`
6. Register view in `backend/app/main.py`

### Adding a Frontend Page

1. Create route in `src/app/` following App Router conventions
2. Use `useQuery` from TanStack Query for data fetching
3. Use Zustand store for client state if needed
4. Import API client from `lib/api.ts` (handles JWT automatically)
5. Follow existing design patterns (dark theme, Framer Motion animations)

## Important Notes

- **Always use async/await** for database operations
- **JWT tokens** are required for all protected endpoints (except auth)
- **Questions and answers are shuffled** on every fetch - don't cache order
- **Score calculation** happens server-side in `crud/scoring.py`
- **Admin users** have `is_admin=True` flag for elevated permissions
- **Celery tasks** run in separate worker container - check `celery_worker` logs
- **Database migrations** must be run manually after model changes
- **CORS** is configured for localhost:3000 - update for production

## Deployment

Production deployment uses `docker-compose.prod.yml` with:
- Nginx reverse proxy
- Frontend standalone build
- Gunicorn for backend
- Separate Celery worker container

See `DEPLOYMENT_GUIDE.md` for detailed production setup.
