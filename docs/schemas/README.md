# Документация схем IT Navigator

Этот каталог содержит полную документацию архитектуры и потоков данных проекта IT Navigator.

## 📋 Содержание

### 1. [Блок-схема всей системы](./01-system-architecture.md)
**Общая архитектура системы**

Описывает высокоуровневую архитектуру всего проекта, включая:
- Клиентский слой (Browser, Mobile)
- Frontend слой (Next.js 14)
- Backend слой (FastAPI)
- Фоновую обработку (Celery)
- Слой данных (PostgreSQL, Redis)
- Потоки аутентификации, тестирования и администрирования
- Компоненты масштабирования
- Безопасность и мониторинг

**Ключевые диаграммы:**
- Общая архитектура системы
- Поток аутентификации пользователя
- Поток прохождения теста
- Административная панель
- Масштабирование и безопасность

---

### 2. [Схема интерфейса](./02-interface-schema.md)
**UI/UX структура и компоненты**

Детальное описание пользовательского интерфейса:
- Структура навигации
- Wireframes основных страниц (Landing, Dashboard, Test, Results, Admin)
- UI Components Library (Atoms, Molecules, Organisms)
- Дизайн-система (цвета, типографика, spacing)
- Responsive design (Mobile, Tablet, Desktop)
- Анимации и переходы
- Accessibility (WCAG 2.1 AA)
- User flows
- Error и Loading states

**Ключевые диаграммы:**
- Структура навигации
- Wireframes всех страниц
- Компонентная библиотека
- User flow прохождения теста

---

### 3. [Схема Frontend архитектуры](./03-frontend-architecture.md)
**Next.js 14 + React архитектура**

Подробная документация Frontend части:
- Структура Next.js App Router
- State Management (Zustand)
- Data Fetching (TanStack Query)
- API Client (Axios)
- Компонентная архитектура
- Routing и Navigation
- Performance Optimization
- Error Handling
- Testing Strategy
- Build и Deploy

**Ключевые диаграммы:**
- Общая структура Frontend
- Структура директорий
- State Management flow
- Data Fetching flow
- API Client configuration
- Component Architecture

**Технологии:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Zustand (State Management)
- TanStack Query (Data Fetching)
- Axios (HTTP Client)
- Tailwind CSS
- Framer Motion

---

### 4. [Схема Backend архитектуры](./04-backend-architecture.md)
**FastAPI + PostgreSQL + Celery архитектура**

Полная документация Backend части:
- Структура FastAPI приложения
- Database Models и связи (SQLAlchemy)
- API Endpoints
- CRUD Operations
- Security Layer (JWT, bcrypt)
- Background Processing (Celery)
- Admin Panel (SQLAdmin)
- Caching Strategy (Redis)
- Logging и Monitoring
- Database Migrations (Alembic)
- Testing Strategy
- Performance Optimization

**Ключевые диаграммы:**
- Общая структура Backend
- Database ER-диаграмма
- API Endpoints flow
- CRUD Operations
- Security Layer
- Celery Tasks
- Admin Panel

**Технологии:**
- FastAPI
- PostgreSQL
- SQLAlchemy (Async)
- Celery
- Redis
- Alembic
- SQLAdmin
- Pydantic
- JWT (jose)
- bcrypt

---

### 5. [Потоки данных](./05-data-flows.md)
**Детальное описание всех потоков данных**

Пошаговое описание всех основных потоков данных в системе:

1. **Поток регистрации пользователя**
   - Валидация на клиенте и сервере
   - Хеширование пароля
   - Генерация JWT token
   - Кэширование сессии

2. **Поток аутентификации (Login)**
   - Проверка credentials
   - Генерация token
   - Обновление last_login

3. **Поток получения вопросов теста**
   - Двухуровневое кэширование
   - Перемешивание вопросов и ответов
   - React Query cache management

4. **Поток прохождения теста**
   - Локальное хранение ответов (Zustand)
   - Навигация между вопросами
   - Sidebar с индикацией прогресса

5. **Поток отправки и обработки результатов**
   - Асинхронная обработка через Celery
   - Расчет баллов
   - Polling для отслеживания прогресса

6. **Поток отображения результатов**
   - Проверка прав доступа
   - Кэширование результатов
   - Визуализация данных

7. **Поток скачивания PDF**
   - Асинхронная генерация
   - Кэширование PDF (24 часа)
   - Polling для отслеживания генерации

8. **Поток работы с Admin Panel**
   - Проверка прав администратора
   - CRUD операции
   - Audit logging

9. **Поток кэширования и инвалидации**
   - Стратегии кэширования
   - TTL для разных типов данных
   - Инвалидация при обновлениях

10. **Поток обработки ошибок**
    - Типы ошибок (500, 422, 401, 403)
    - Retry механизмы
    - Error reporting (Sentry)

11. **Поток WebSocket (будущее)**
    - Real-time обновления
    - Redis PubSub
    - Progress tracking

**Таблицы:**
- Стратегии кэширования с TTL
- Типы ошибок и их обработка
- Синхронные vs Асинхронные потоки

---

## 🎯 Как использовать эту документацию

### Для новых разработчиков
1. Начните с [01-system-architecture.md](./01-system-architecture.md) для понимания общей картины
2. Изучите [05-data-flows.md](./05-data-flows.md) для понимания взаимодействия компонентов
3. Перейдите к [03-frontend-architecture.md](./03-frontend-architecture.md) или [04-backend-architecture.md](./04-backend-architecture.md) в зависимости от вашей роли

### Для Frontend разработчиков
1. [02-interface-schema.md](./02-interface-schema.md) - UI/UX структура
2. [03-frontend-architecture.md](./03-frontend-architecture.md) - техническая архитектура
3. [05-data-flows.md](./05-data-flows.md) - потоки данных (секции 1-7)

### Для Backend разработчиков
1. [04-backend-architecture.md](./04-backend-architecture.md) - техническая архитектура
2. [05-data-flows.md](./05-data-flows.md) - потоки данных (секции 1-10)
3. [01-system-architecture.md](./01-system-architecture.md) - интеграция с другими компонентами

### Для DevOps инженеров
1. [01-system-architecture.md](./01-system-architecture.md) - инфраструктура и масштабирование
2. [04-backend-architecture.md](./04-backend-architecture.md) - Backend deployment
3. [03-frontend-architecture.md](./03-frontend-architecture.md) - Frontend build & deploy

### Для UI/UX дизайнеров
1. [02-interface-schema.md](./02-interface-schema.md) - полная UI документация
2. [05-data-flows.md](./05-data-flows.md) - user flows (секция 4)

### Для Product Managers
1. [01-system-architecture.md](./01-system-architecture.md) - общая архитектура
2. [02-interface-schema.md](./02-interface-schema.md) - user experience
3. [05-data-flows.md](./05-data-flows.md) - бизнес-процессы

---

## 📊 Диаграммы

Все диаграммы созданы с использованием **Mermaid** и могут быть отрендерены в:
- GitHub (нативная поддержка)
- VS Code (с расширением Mermaid)
- Онлайн редакторах (mermaid.live)

### Типы диаграмм
- **Graph/Flowchart** - архитектурные схемы
- **Sequence Diagram** - потоки взаимодействия
- **ER Diagram** - модели базы данных
- **State Diagram** - user flows

---

## 🔄 Обновление документации

При внесении изменений в архитектуру:

1. **Обновите соответствующий файл схемы**
2. **Обновите связанные диаграммы**
3. **Проверьте консистентность с другими документами**
4. **Обновите дату последнего изменения**

### Контрольный список изменений

- [ ] Обновлены диаграммы Mermaid
- [ ] Обновлены текстовые описания
- [ ] Проверена консистентность с кодом
- [ ] Обновлены связанные документы
- [ ] Добавлены примеры кода (если нужно)

---

## 📝 Связанные документы

- [CLAUDE.md](../../CLAUDE.md) - Инструкции для Claude Code
- [README.md](../../README.md) - Основная документация проекта
- [DEPLOYMENT_GUIDE.md](../../DEPLOYMENT_GUIDE.md) - Руководство по развертыванию

---

## 🛠️ Технологический стек

### Frontend
- Next.js 14 (App Router)
- React 18
- TypeScript
- Zustand
- TanStack Query
- Axios
- Tailwind CSS
- Framer Motion

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy (Async)
- Celery
- Redis
- Alembic
- SQLAdmin
- Pydantic

### Infrastructure
- Docker & Docker Compose
- Nginx
- Redis
- PostgreSQL

### DevOps
- GitHub Actions (CI/CD)
- Docker
- Nginx
- Prometheus (monitoring)
- Sentry (error tracking)

---

## 📞 Контакты

Если у вас есть вопросы по архитектуре или документации:
- Создайте Issue в репозитории
- Обратитесь к команде разработки

---

**Последнее обновление:** 2026-05-26

**Версия документации:** 1.0.0
