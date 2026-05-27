# Career Platform - Профориентационная платформа

Полнофункциональная платформа для профориентационного тестирования с адаптивными тестами и детальной аналитикой результатов.

## Архитектура

- **Backend**: FastAPI + PostgreSQL + SQLAlchemy (async)
- **Admin Panel**: SQLAdmin
- **Auth**: JWT tokens
- **Database**: PostgreSQL 16
- **Containerization**: Docker + Docker Compose

## Быстрый старт

### 1. Настройка

```bash
cd IT-Navigator

# Создать .env файл
cp backend/.env.example backend/.env

# Отредактировать backend/.env и установить SECRET_KEY
# Можно сгенерировать: openssl rand -hex 32
```

### 2. Запуск через Docker Compose

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f backend
```

### 3. Инициализация базы данных

```bash
# Создать все данные (админ, специальности, тесты)
# Скрипт полностью самодостаточный - все тесты захардкожены внутри
docker-compose exec backend python -m scripts.init_db

# Это создаст:
# - Админ пользователя (admin@example.com / admin123)
# - 7 IT-специальностей (F1-F7)
# - Общий тест (13 вопросов)
# - 7 специализированных тестов (по 10 вопросов каждый)
```

### 4. Доступ к приложению

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin
  - Email: `admin@example.com`
  - Password: `admin123`

## Деплой на VPS

Для деплоя на продакшн сервер смотрите подробную инструкцию в [DEPLOYMENT.md](DEPLOYMENT.md).

Краткая версия:
```bash
# 1. Настроить .env файлы
# 2. Запустить сервисы
docker compose up -d

# 3. Инициализировать БД (все тесты уже внутри скрипта!)
docker compose exec backend python -m scripts.init_db

# Готово! Все тесты загружены автоматически.
```

**Важно**: Скрипт `init_db.py` полностью самодостаточный и содержит все тесты внутри. Не нужны никакие внешние файлы!

- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health

**Учётные данные админа:**
- Email: `admin@example.com`
- Password: `admin123`

## API Endpoints

### Авторизация

```bash
# Регистрация
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "full_name": "Test User"}'

# Вход (получение токена)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

### Тестирование

```bash
# Получить вопросы общего теста
curl http://localhost:8000/api/v1/tests/general/questions \
  -H "Authorization: Bearer <token>"

# Отправить ответы
curl -X POST http://localhost:8000/api/v1/tests/general/submit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"answers": [{"question_id": 1, "answer_id": 1}]}'

# Получить историю результатов
curl http://localhost:8000/api/v1/tests/results/my \
  -H "Authorization: Bearer <token>"
```

## Roadmap

### ✅ Блок 1 - Фундамент (Завершён)
- Docker Compose с PostgreSQL
- SQLAlchemy модели (User, Specialty, Test, Question, Answer, TestResult)
- Alembic миграции
- JWT авторизация
- SQLAdmin панель

### ✅ Блок 2 - Ядро тестирования (Завершён)
- API получения вопросов с перемешиванием
- Алгоритм подсчёта баллов по специальностям
- Сохранение результатов в БД
- История прохождений пользователя

### 🔄 Блок 3 - Фронтенд (В планах)
- Next.js 14 + TypeScript
- React Query + Zustand
- Tailwind CSS

### 🔄 Блок 4 - Фоновые задачи (В планах)
- Redis + Celery
- Кэширование вопросов
- PDF отчёты

### 🔄 Блок 5 - Стабилизация (В планах)
- Pytest покрытие
- CI/CD
- Production config

## Документация

Подробная документация в `backend/README.md`

## Лицензия

MIT
