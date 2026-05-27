# Блок-схема всей системы IT Navigator

## Общая архитектура системы

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        Mobile[Mobile Browser]
    end

    subgraph "Frontend Layer - Next.js 14"
        NextApp[Next.js App Router]
        Pages[Pages/Routes]
        Components[React Components]
        StateManagement[Zustand Store]
        ReactQuery[TanStack Query]
        APIClient[Axios Client + JWT]
    end

    subgraph "Reverse Proxy"
        Nginx[Nginx]
    end

    subgraph "Backend Layer - FastAPI"
        FastAPI[FastAPI Application]
        
        subgraph "API Endpoints"
            AuthAPI[Auth Endpoints]
            TestsAPI[Tests Endpoints]
            ResultsAPI[Results Endpoints]
        end
        
        subgraph "Business Logic"
            CRUD[CRUD Operations]
            Scoring[Score Calculation]
            Security[JWT & Security]
        end
        
        subgraph "Admin Panel"
            SQLAdmin[SQLAdmin Interface]
        end
    end

    subgraph "Background Processing"
        Celery[Celery Worker]
        CeleryTasks[Background Tasks]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database)]
        Redis[(Redis Cache)]
    end

    subgraph "Database Models"
        User[User Model]
        Specialty[Specialty Model]
        Test[Test Model]
        Question[Question Model]
        Answer[Answer Model]
        Result[TestResult Model]
    end

    %% Client connections
    Browser --> NextApp
    Mobile --> NextApp

    %% Frontend flow
    NextApp --> Pages
    Pages --> Components
    Components --> StateManagement
    Components --> ReactQuery
    ReactQuery --> APIClient

    %% Network flow
    APIClient --> Nginx
    Nginx --> FastAPI

    %% Backend flow
    FastAPI --> AuthAPI
    FastAPI --> TestsAPI
    FastAPI --> ResultsAPI
    FastAPI --> SQLAdmin

    AuthAPI --> Security
    TestsAPI --> CRUD
    ResultsAPI --> CRUD

    CRUD --> Scoring
    Security --> CRUD

    %% Background processing
    FastAPI --> Celery
    Celery --> CeleryTasks
    CeleryTasks --> Scoring

    %% Data connections
    CRUD --> PostgreSQL
    Scoring --> PostgreSQL
    SQLAdmin --> PostgreSQL
    
    Celery --> Redis
    FastAPI --> Redis

    %% Database models
    PostgreSQL --> User
    PostgreSQL --> Specialty
    PostgreSQL --> Test
    PostgreSQL --> Question
    PostgreSQL --> Answer
    PostgreSQL --> Result

    %% Styling
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px,color:#000
    classDef backend fill:#009688,stroke:#333,stroke-width:2px,color:#fff
    classDef database fill:#336791,stroke:#333,stroke-width:2px,color:#fff
    classDef worker fill:#37b24d,stroke:#333,stroke-width:2px,color:#fff
    classDef proxy fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff

    class NextApp,Pages,Components,StateManagement,ReactQuery,APIClient frontend
    class FastAPI,AuthAPI,TestsAPI,ResultsAPI,CRUD,Scoring,Security,SQLAdmin backend
    class PostgreSQL,Redis,User,Specialty,Test,Question,Answer,Result database
    class Celery,CeleryTasks worker
    class Nginx proxy
```

## Потоки данных

### 1. Аутентификация пользователя

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant N as Nginx
    participant B as Backend API
    participant DB as PostgreSQL
    participant R as Redis

    U->>F: Ввод логина/пароля
    F->>N: POST /api/v1/auth/login
    N->>B: Проксирование запроса
    B->>DB: Проверка credentials
    DB-->>B: User data
    B->>B: Генерация JWT token
    B->>R: Кэширование сессии
    B-->>N: JWT token
    N-->>F: JWT token
    F->>F: Сохранение в localStorage
    F-->>U: Редирект на dashboard
```

### 2. Прохождение теста

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend API
    participant DB as PostgreSQL
    participant C as Celery Worker
    participant R as Redis

    U->>F: Начать тест
    F->>B: GET /tests/general/questions
    B->>DB: Получить вопросы
    DB-->>B: Questions + Answers
    B->>B: Перемешать вопросы/ответы
    B-->>F: Shuffled questions
    F-->>U: Отображение вопросов

    U->>F: Отправка ответов
    F->>B: POST /tests/general/submit
    B->>R: Добавить задачу в очередь
    B-->>F: Task ID
    
    C->>R: Получить задачу
    C->>DB: Получить веса ответов
    C->>C: Расчет баллов
    C->>DB: Сохранить результат
    C-->>R: Задача выполнена

    F->>B: GET /tests/results/{id}
    B->>DB: Получить результат
    DB-->>B: Test result
    B-->>F: Result data
    F-->>U: Отображение результатов
```

### 3. Административная панель

```mermaid
sequenceDiagram
    participant A as Admin
    participant SA as SQLAdmin
    participant B as Backend
    participant DB as PostgreSQL

    A->>SA: Вход в /admin
    SA->>B: Проверка is_admin
    B->>DB: Проверка прав
    DB-->>B: Admin status
    B-->>SA: Доступ разрешен
    SA-->>A: Admin interface

    A->>SA: CRUD операции
    SA->>DB: SQL запросы
    DB-->>SA: Результат
    SA-->>A: Обновленные данные
```

## Компоненты системы

### Frontend (Next.js 14)
- **App Router**: Маршрутизация на основе файловой системы
- **React Components**: Переиспользуемые UI компоненты
- **Zustand**: Управление состоянием клиента
- **TanStack Query**: Кэширование и синхронизация данных с сервером
- **Axios**: HTTP клиент с JWT interceptor

### Backend (FastAPI)
- **API Endpoints**: RESTful API с автодокументацией
- **SQLAlchemy**: Async ORM для работы с БД
- **JWT Authentication**: Токен-based аутентификация
- **Pydantic**: Валидация данных и схемы
- **SQLAdmin**: Административная панель

### Background Processing (Celery)
- **Celery Worker**: Асинхронная обработка задач
- **Redis**: Брокер сообщений и кэш
- **Tasks**: Расчет баллов, генерация PDF

### Database (PostgreSQL)
- **Users**: Пользователи системы
- **Specialties**: IT-специальности (F1-F7)
- **Tests**: Общие и специализированные тесты
- **Questions**: Вопросы тестов
- **Answers**: Варианты ответов с весами
- **TestResults**: Результаты прохождения тестов

### Infrastructure
- **Docker Compose**: Оркестрация контейнеров
- **Nginx**: Reverse proxy и статика
- **Redis**: Кэш и очередь задач

## Масштабирование

```mermaid
graph LR
    subgraph "Load Balancer"
        LB[Nginx Load Balancer]
    end

    subgraph "Frontend Instances"
        F1[Next.js Instance 1]
        F2[Next.js Instance 2]
        F3[Next.js Instance N]
    end

    subgraph "Backend Instances"
        B1[FastAPI Instance 1]
        B2[FastAPI Instance 2]
        B3[FastAPI Instance N]
    end

    subgraph "Worker Pool"
        W1[Celery Worker 1]
        W2[Celery Worker 2]
        W3[Celery Worker N]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL Primary)]
        DBR[(PostgreSQL Replica)]
        Redis[(Redis Cluster)]
    end

    LB --> F1
    LB --> F2
    LB --> F3

    F1 --> LB
    F2 --> LB
    F3 --> LB

    LB --> B1
    LB --> B2
    LB --> B3

    B1 --> DB
    B2 --> DB
    B3 --> DB

    B1 --> Redis
    B2 --> Redis
    B3 --> Redis

    W1 --> Redis
    W2 --> Redis
    W3 --> Redis

    W1 --> DB
    W2 --> DB
    W3 --> DB

    DB -.Репликация.-> DBR
```

## Безопасность

```mermaid
graph TB
    subgraph "Security Layers"
        HTTPS[HTTPS/TLS]
        CORS[CORS Policy]
        JWT[JWT Authentication]
        Hash[Password Hashing]
        Validation[Input Validation]
        RateLimit[Rate Limiting]
    end

    subgraph "Attack Prevention"
        SQLi[SQL Injection Prevention]
        XSS[XSS Protection]
        CSRF[CSRF Protection]
    end

    HTTPS --> CORS
    CORS --> JWT
    JWT --> Hash
    Hash --> Validation
    Validation --> RateLimit

    Validation --> SQLi
    Validation --> XSS
    JWT --> CSRF
```

## Мониторинг и логирование

```mermaid
graph LR
    subgraph "Application"
        App[FastAPI App]
        Worker[Celery Worker]
    end

    subgraph "Monitoring"
        Logs[Application Logs]
        Metrics[Prometheus Metrics]
        Flower[Flower Dashboard]
    end

    subgraph "Alerting"
        Alerts[Alert Manager]
        Notifications[Notifications]
    end

    App --> Logs
    App --> Metrics
    Worker --> Flower
    Worker --> Logs

    Metrics --> Alerts
    Alerts --> Notifications
```
