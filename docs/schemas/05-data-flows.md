# Потоки данных IT Navigator

## Обзор потоков данных

Этот документ описывает все основные потоки данных в системе IT Navigator, включая взаимодействие между компонентами, обработку запросов и управление состоянием.

## 1. Поток регистрации пользователя

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant NextJS as Next.js Frontend
    participant Nginx
    participant FastAPI as FastAPI Backend
    participant DB as PostgreSQL
    participant Redis

    User->>Browser: Заполняет форму регистрации
    Browser->>NextJS: Отправка формы
    NextJS->>NextJS: Валидация на клиенте
    
    NextJS->>Nginx: POST /api/v1/auth/register
    Note over NextJS,Nginx: {email, password, full_name}
    
    Nginx->>FastAPI: Проксирование запроса
    FastAPI->>FastAPI: Валидация Pydantic схемы
    
    FastAPI->>DB: Проверка существования email
    DB-->>FastAPI: Email не существует
    
    FastAPI->>FastAPI: Хеширование пароля (bcrypt)
    FastAPI->>DB: INSERT INTO users
    DB-->>FastAPI: User created (id, email, full_name)
    
    FastAPI->>FastAPI: Генерация JWT token
    Note over FastAPI: payload: {sub: user_id, exp: timestamp}
    
    FastAPI->>Redis: Сохранение сессии
    Note over FastAPI,Redis: key: session:{user_id}, ttl: 24h
    
    FastAPI-->>Nginx: 201 Created
    Note over FastAPI,Nginx: {token, user: {id, email, full_name}}
    
    Nginx-->>NextJS: Response
    NextJS->>NextJS: Сохранение token в localStorage
    NextJS->>NextJS: Обновление auth store (Zustand)
    NextJS-->>Browser: Редирект на /dashboard
    Browser-->>User: Показ dashboard
```

**Ключевые моменты:**
- Валидация происходит на двух уровнях: клиент (React Hook Form) и сервер (Pydantic)
- Пароль хешируется с использованием bcrypt (cost factor: 12)
- JWT token содержит только user_id и expiration
- Сессия кэшируется в Redis для быстрой валидации
- Token сохраняется в localStorage и автоматически добавляется к запросам через Axios interceptor

## 2. Поток аутентификации (Login)

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant NextJS as Next.js Frontend
    participant Nginx
    participant FastAPI as FastAPI Backend
    participant DB as PostgreSQL
    participant Redis

    User->>Browser: Ввод email/password
    Browser->>NextJS: Отправка формы
    
    NextJS->>Nginx: POST /api/v1/auth/login
    Note over NextJS,Nginx: {email, password}
    
    Nginx->>FastAPI: Проксирование
    FastAPI->>DB: SELECT * FROM users WHERE email = ?
    DB-->>FastAPI: User data (id, email, hashed_password)
    
    FastAPI->>FastAPI: Проверка пароля
    Note over FastAPI: bcrypt.verify(password, hashed_password)
    
    alt Пароль верный
        FastAPI->>FastAPI: Генерация JWT token
        FastAPI->>Redis: Сохранение сессии
        Redis-->>FastAPI: OK
        
        FastAPI->>DB: UPDATE users SET last_login = NOW()
        DB-->>FastAPI: Updated
        
        FastAPI-->>Nginx: 200 OK {token, user}
        Nginx-->>NextJS: Response
        
        NextJS->>NextJS: localStorage.setItem('token', token)
        NextJS->>NextJS: authStore.login(user)
        NextJS-->>Browser: Редирект на /dashboard
        
    else Пароль неверный
        FastAPI-->>Nginx: 401 Unauthorized
        Nginx-->>NextJS: Error response
        NextJS-->>Browser: Показ ошибки
    end
```

**Ключевые моменты:**
- Используется OAuth2PasswordBearer для стандартизации
- При неудачной попытке логина не раскрывается, существует ли email
- Last login timestamp обновляется при успешном входе
- Token автоматически добавляется ко всем последующим запросам

## 3. Поток получения вопросов теста

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant NextJS as Next.js Frontend
    participant ReactQuery as TanStack Query
    participant Nginx
    participant FastAPI as FastAPI Backend
    participant Redis
    participant DB as PostgreSQL

    User->>Browser: Клик "Начать тест"
    Browser->>NextJS: Навигация на /test/general
    
    NextJS->>ReactQuery: useQuery(['tests', 'general'])
    ReactQuery->>ReactQuery: Проверка cache
    
    alt Cache miss
        ReactQuery->>Nginx: GET /api/v1/tests/general/questions
        Note over ReactQuery,Nginx: Authorization: Bearer {token}
        
        Nginx->>FastAPI: Проксирование
        FastAPI->>FastAPI: Валидация JWT token
        FastAPI->>FastAPI: get_current_user()
        
        FastAPI->>Redis: Проверка cache
        Note over FastAPI,Redis: key: test:general:questions
        
        alt Cache miss
            FastAPI->>DB: SELECT questions with answers
            Note over FastAPI,DB: JOIN questions, answers, specialties
            DB-->>FastAPI: Questions array
            
            FastAPI->>FastAPI: Перемешивание вопросов
            Note over FastAPI: random.shuffle(questions)
            
            FastAPI->>FastAPI: Перемешивание ответов
            Note over FastAPI: for q in questions: random.shuffle(q.answers)
            
            FastAPI->>Redis: Кэширование результата
            Note over FastAPI,Redis: ttl: 5 minutes
        else Cache hit
            Redis-->>FastAPI: Cached questions
        end
        
        FastAPI-->>Nginx: 200 OK {questions: [...]}
        Nginx-->>ReactQuery: Response
        
        ReactQuery->>ReactQuery: Кэширование в Query Cache
        Note over ReactQuery: staleTime: 0 (always fresh)
        
    else Cache hit
        ReactQuery->>ReactQuery: Возврат из cache
    end
    
    ReactQuery-->>NextJS: Questions data
    NextJS->>NextJS: testStore.setQuestions(questions)
    NextJS-->>Browser: Рендер вопросов
    Browser-->>User: Отображение первого вопроса
```

**Ключевые моменты:**
- Двухуровневое кэширование: Redis (backend) + React Query (frontend)
- Вопросы и ответы перемешиваются на сервере для предотвращения запоминания
- React Query не кэширует результат (staleTime: 0), так как каждый запрос должен возвращать новый порядок
- Redis cache используется для снижения нагрузки на БД при множественных запросах

## 4. Поток прохождения теста

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant NextJS as Next.js Frontend
    participant TestStore as Zustand Test Store
    participant ReactQuery as TanStack Query

    User->>Browser: Просмотр вопроса 1
    Browser->>NextJS: Отображение QuestionCard
    
    User->>Browser: Выбор ответа
    Browser->>NextJS: onClick handler
    NextJS->>TestStore: setAnswer(questionId, answerId)
    TestStore->>TestStore: answers[questionId] = [answerId]
    TestStore-->>NextJS: State updated
    NextJS-->>Browser: UI update (выделение ответа)
    
    User->>Browser: Клик "Далее"
    Browser->>NextJS: nextQuestion()
    NextJS->>TestStore: currentQuestionIndex++
    TestStore-->>NextJS: New index
    NextJS-->>Browser: Рендер следующего вопроса
    
    Note over User,ReactQuery: ... пользователь отвечает на все вопросы ...
    
    User->>Browser: Клик "Завершить тест"
    Browser->>NextJS: Показ модального окна подтверждения
    
    User->>Browser: Подтверждение
    Browser->>NextJS: submitTest()
    NextJS->>TestStore: Получение всех ответов
    TestStore-->>NextJS: answers object
    
    NextJS->>ReactQuery: useMutation(submitTest)
    ReactQuery->>ReactQuery: Показ loading state
    NextJS-->>Browser: Показ spinner
```

**Ключевые моменты:**
- Все ответы хранятся локально в Zustand store
- Нет автосохранения на сервер (все отправляется одним запросом)
- Пользователь может вернуться к предыдущим вопросам и изменить ответы
- Sidebar показывает статус каждого вопроса (отвечен/не отвечен)

## 5. Поток отправки и обработки результатов теста

```mermaid
sequenceDiagram
    participant NextJS as Next.js Frontend
    participant Nginx
    participant FastAPI as FastAPI Backend
    participant Redis
    participant Celery as Celery Worker
    participant DB as PostgreSQL

    NextJS->>Nginx: POST /api/v1/tests/general/submit
    Note over NextJS,Nginx: {answers: {question_id: [answer_ids]}}
    
    Nginx->>FastAPI: Проксирование
    FastAPI->>FastAPI: Валидация JWT + get_current_user()
    FastAPI->>FastAPI: Валидация структуры ответов
    
    FastAPI->>DB: BEGIN TRANSACTION
    
    FastAPI->>DB: INSERT INTO test_results
    Note over FastAPI,DB: user_id, test_id, answers, started_at
    DB-->>FastAPI: result_id
    
    FastAPI->>Redis: Добавление задачи в очередь
    Note over FastAPI,Redis: task: calculate_scores(result_id)
    Redis-->>FastAPI: task_id
    
    FastAPI->>DB: COMMIT TRANSACTION
    
    FastAPI-->>Nginx: 202 Accepted
    Note over FastAPI,Nginx: {result_id, task_id, status: 'processing'}
    Nginx-->>NextJS: Response
    
    NextJS->>NextJS: Навигация на /results/{result_id}
    NextJS->>NextJS: Показ loading state
    
    par Асинхронная обработка
        Celery->>Redis: Получение задачи из очереди
        Redis-->>Celery: Task data
        
        Celery->>DB: SELECT answers with weights
        Note over Celery,DB: JOIN answers, questions, specialties
        DB-->>Celery: Answer weights
        
        Celery->>Celery: Расчет баллов
        Note over Celery: for each answer:<br/>scores[specialty] += weight
        
        Celery->>Celery: Нормализация баллов (0-100)
        Note over Celery: normalized = (score / max_score) * 100
        
        Celery->>DB: UPDATE test_results
        Note over Celery,DB: SET scores = {...}, completed_at = NOW()
        DB-->>Celery: Updated
        
        Celery->>Redis: Обновление статуса задачи
        Redis-->>Celery: OK
        
        Celery->>Celery: Запуск дополнительных задач
        Note over Celery: - generate_pdf(result_id)<br/>- send_notification(result_id)
    end
    
    NextJS->>Nginx: Polling: GET /api/v1/tests/results/{result_id}
    Nginx->>FastAPI: Проксирование
    FastAPI->>DB: SELECT * FROM test_results WHERE id = ?
    DB-->>FastAPI: Result data
    
    alt Обработка завершена
        FastAPI-->>Nginx: 200 OK {result with scores}
        Nginx-->>NextJS: Response
        NextJS->>NextJS: Отображение результатов
    else Обработка в процессе
        FastAPI-->>Nginx: 200 OK {status: 'processing'}
        Nginx-->>NextJS: Response
        NextJS->>NextJS: Продолжение polling
    end
```

**Ключевые моменты:**
- Асинхронная обработка через Celery для тяжелых вычислений
- Немедленный ответ клиенту (202 Accepted) с последующим polling
- Транзакционная безопасность при создании результата
- Retry механизм в Celery для обработки ошибок
- Дополнительные задачи (PDF, email) запускаются после основной обработки

## 6. Поток отображения результатов

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant NextJS as Next.js Frontend
    participant ReactQuery as TanStack Query
    participant Nginx
    participant FastAPI as FastAPI Backend
    participant DB as PostgreSQL

    User->>Browser: Навигация на /results/{id}
    Browser->>NextJS: Page load
    
    NextJS->>ReactQuery: useQuery(['results', id])
    ReactQuery->>Nginx: GET /api/v1/tests/results/{id}
    
    Nginx->>FastAPI: Проксирование
    FastAPI->>FastAPI: Валидация JWT + get_current_user()
    
    FastAPI->>DB: SELECT result with relations
    Note over FastAPI,DB: JOIN test_results, tests, users
    DB-->>FastAPI: Result data
    
    FastAPI->>FastAPI: Проверка ownership
    Note over FastAPI: result.user_id == current_user.id<br/>OR current_user.is_admin
    
    alt Доступ разрешен
        FastAPI-->>Nginx: 200 OK {result}
        Nginx-->>ReactQuery: Response
        
        ReactQuery->>ReactQuery: Кэширование
        Note over ReactQuery: staleTime: 1 minute
        
        ReactQuery-->>NextJS: Result data
        
        NextJS->>NextJS: Обработка данных для визуализации
        Note over NextJS: - Сортировка специальностей по баллам<br/>- Подготовка данных для Radar Chart<br/>- Генерация рекомендаций
        
        NextJS-->>Browser: Рендер компонентов
        
        Browser->>Browser: Анимация появления
        Note over Browser: Framer Motion animations
        
        Browser-->>User: Отображение результатов
        
    else Доступ запрещен
        FastAPI-->>Nginx: 403 Forbidden
        Nginx-->>ReactQuery: Error
        ReactQuery-->>NextJS: Error state
        NextJS-->>Browser: Показ ошибки
    end
```

**Ключевые моменты:**
- Проверка прав доступа на уровне API (только владелец или админ)
- Кэширование результатов в React Query (1 минута)
- Клиентская обработка данных для визуализации
- Анимации для улучшения UX

## 7. Поток скачивания PDF

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant NextJS as Next.js Frontend
    participant Nginx
    participant FastAPI as FastAPI Backend
    participant Redis
    participant Celery as Celery Worker
    participant Storage as File Storage

    User->>Browser: Клик "Скачать PDF"
    Browser->>NextJS: onClick handler
    
    NextJS->>Nginx: POST /api/v1/tests/results/{id}/pdf
    Nginx->>FastAPI: Проксирование
    
    FastAPI->>FastAPI: Валидация прав доступа
    
    FastAPI->>Redis: Проверка существующего PDF
    Note over FastAPI,Redis: key: pdf:{result_id}
    
    alt PDF уже существует
        Redis-->>FastAPI: PDF URL
        FastAPI-->>Nginx: 200 OK {pdf_url}
        Nginx-->>NextJS: Response
        NextJS->>Browser: window.open(pdf_url)
        
    else PDF не существует
        FastAPI->>Redis: Добавление задачи
        Note over FastAPI,Redis: task: generate_pdf(result_id)
        Redis-->>FastAPI: task_id
        
        FastAPI-->>Nginx: 202 Accepted {task_id}
        Nginx-->>NextJS: Response
        NextJS-->>Browser: Показ "Генерация PDF..."
        
        par Генерация PDF
            Celery->>Redis: Получение задачи
            Celery->>FastAPI: GET result data (internal)
            FastAPI-->>Celery: Result data
            
            Celery->>Celery: Генерация PDF
            Note over Celery: - Создание документа<br/>- Добавление графиков<br/>- Форматирование текста
            
            Celery->>Storage: Сохранение PDF
            Storage-->>Celery: File path
            
            Celery->>Redis: Кэширование URL
            Note over Celery,Redis: key: pdf:{result_id}, ttl: 24h
            
            Celery->>Redis: Обновление статуса
        end
        
        NextJS->>Nginx: Polling: GET /api/v1/tasks/{task_id}
        Nginx->>FastAPI: Проксирование
        FastAPI->>Redis: Проверка статуса
        
        alt PDF готов
            Redis-->>FastAPI: {status: 'completed', pdf_url}
            FastAPI-->>Nginx: 200 OK {pdf_url}
            Nginx-->>NextJS: Response
            NextJS->>Browser: window.open(pdf_url)
            Browser-->>User: Скачивание PDF
            
        else Генерация в процессе
            Redis-->>FastAPI: {status: 'processing'}
            FastAPI-->>Nginx: 200 OK {status}
            Nginx-->>NextJS: Response
            NextJS->>NextJS: Продолжение polling
        end
    end
```

**Ключевые моменты:**
- Кэширование сгенерированных PDF (24 часа)
- Асинхронная генерация для больших документов
- Polling для отслеживания прогресса
- Хранение файлов в отдельном storage (может быть S3, local filesystem)

## 8. Поток работы с Admin Panel

```mermaid
sequenceDiagram
    actor Admin
    participant Browser
    participant SQLAdmin as SQLAdmin Interface
    participant FastAPI as FastAPI Backend
    participant DB as PostgreSQL

    Admin->>Browser: Навигация на /admin
    Browser->>SQLAdmin: GET /admin
    
    SQLAdmin->>FastAPI: Проверка аутентификации
    FastAPI->>FastAPI: Валидация JWT
    FastAPI->>FastAPI: Проверка is_admin flag
    
    alt Пользователь - админ
        FastAPI-->>SQLAdmin: Access granted
        SQLAdmin-->>Browser: Рендер admin interface
        Browser-->>Admin: Показ списка моделей
        
        Admin->>Browser: Выбор модели (Users)
        Browser->>SQLAdmin: GET /admin/users
        
        SQLAdmin->>DB: SELECT * FROM users
        Note over SQLAdmin,DB: С пагинацией, фильтрами, сортировкой
        DB-->>SQLAdmin: Users data
        
        SQLAdmin-->>Browser: Рендер таблицы
        Browser-->>Admin: Показ списка пользователей
        
        Admin->>Browser: Клик "Edit" на пользователе
        Browser->>SQLAdmin: GET /admin/users/{id}/edit
        
        SQLAdmin->>DB: SELECT * FROM users WHERE id = ?
        DB-->>SQLAdmin: User data
        
        SQLAdmin-->>Browser: Рендер формы редактирования
        Browser-->>Admin: Показ формы
        
        Admin->>Browser: Изменение данных + Submit
        Browser->>SQLAdmin: POST /admin/users/{id}/edit
        
        SQLAdmin->>SQLAdmin: Валидация данных
        SQLAdmin->>DB: UPDATE users SET ... WHERE id = ?
        DB-->>SQLAdmin: Updated
        
        SQLAdmin-->>Browser: Redirect to list
        Browser-->>Admin: Показ обновленного списка
        
    else Пользователь не админ
        FastAPI-->>SQLAdmin: 403 Forbidden
        SQLAdmin-->>Browser: Redirect to /dashboard
    end
```

**Ключевые моменты:**
- Двойная проверка прав: JWT + is_admin flag
- CRUD операции через SQLAdmin ORM
- Автоматическая валидация через SQLAlchemy models
- Поддержка фильтрации, сортировки, пагинации
- Audit log для отслеживания изменений (опционально)

## 9. Поток кэширования и инвалидации

```mermaid
graph TB
    subgraph "Cache Write Flow"
        Request[API Request]
        CheckCache{Cache<br/>exists?}
        GetFromDB[Get from Database]
        WriteCache[Write to Cache]
        ReturnData[Return Data]
        
        Request --> CheckCache
        CheckCache -->|No| GetFromDB
        CheckCache -->|Yes| ReturnData
        GetFromDB --> WriteCache
        WriteCache --> ReturnData
    end
    
    subgraph "Cache Invalidation Flow"
        DataUpdate[Data Update]
        InvalidateCache[Invalidate Cache]
        UpdateDB[Update Database]
        NotifyClients[Notify Clients]
        
        DataUpdate --> InvalidateCache
        InvalidateCache --> UpdateDB
        UpdateDB --> NotifyClients
    end
    
    subgraph "Cache Layers"
        RedisCache[Redis Cache<br/>Backend]
        ReactQueryCache[React Query Cache<br/>Frontend]
        BrowserCache[Browser Cache<br/>Static Assets]
    end
    
    WriteCache --> RedisCache
    ReturnData --> ReactQueryCache
    NotifyClients --> ReactQueryCache
```

**Стратегии кэширования:**

| Тип данных | Backend Cache (Redis) | Frontend Cache (React Query) | TTL |
|------------|----------------------|------------------------------|-----|
| Test Questions | 5 минут | 0 (always fresh) | Короткий |
| User Session | 24 часа | 5 минут | Длинный |
| Test Results | 10 минут | 1 минута | Средний |
| Specialty Data | 1 час | 10 минут | Длинный |
| Static Content | - | Infinity | Постоянный |

**Инвалидация кэша:**
- При обновлении данных через Admin Panel
- При создании нового результата теста
- При изменении профиля пользователя
- Автоматическая инвалидация по TTL

## 10. Поток обработки ошибок

```mermaid
sequenceDiagram
    participant Client
    participant Frontend
    participant Backend
    participant DB
    participant Sentry

    Client->>Frontend: User action
    Frontend->>Backend: API Request
    
    alt Database Error
        Backend->>DB: Query
        DB-->>Backend: Connection Error
        Backend->>Backend: Log error
        Backend->>Sentry: Send error report
        Backend-->>Frontend: 500 Internal Server Error
        Frontend->>Frontend: Show error toast
        Frontend->>Frontend: Retry logic (3 attempts)
        
    else Validation Error
        Backend->>Backend: Pydantic validation
        Backend-->>Frontend: 422 Unprocessable Entity
        Frontend->>Frontend: Show field errors
        Frontend-->>Client: Highlight invalid fields
        
    else Authentication Error
        Backend->>Backend: JWT validation failed
        Backend-->>Frontend: 401 Unauthorized
        Frontend->>Frontend: Clear auth state
        Frontend->>Frontend: Redirect to /login
        Frontend-->>Client: Show login page
        
    else Authorization Error
        Backend->>Backend: Permission check failed
        Backend-->>Frontend: 403 Forbidden
        Frontend->>Frontend: Show error page
        Frontend-->>Client: "Access Denied"
        
    else Network Error
        Frontend->>Frontend: Request timeout
        Frontend->>Frontend: Show retry button
        Frontend-->>Client: "Network error, please retry"
    end
```

**Обработка ошибок:**
- **500 Errors**: Логирование + отправка в Sentry + retry
- **422 Errors**: Показ inline validation errors
- **401 Errors**: Очистка auth state + редирект на login
- **403 Errors**: Показ страницы "Access Denied"
- **Network Errors**: Retry с exponential backoff

## 11. Поток WebSocket (Real-time Updates) - Будущее расширение

```mermaid
sequenceDiagram
    participant Client
    participant WebSocket
    participant Backend
    participant Redis PubSub
    participant Celery

    Client->>WebSocket: Connect
    WebSocket->>Backend: Authenticate
    Backend->>Backend: Validate JWT
    Backend-->>WebSocket: Connection established
    
    Client->>WebSocket: Subscribe to result updates
    WebSocket->>Redis PubSub: Subscribe channel:result:{id}
    
    par Background Processing
        Celery->>Celery: Calculate scores
        Celery->>Redis PubSub: Publish update
        Note over Celery,Redis PubSub: channel:result:{id}<br/>{progress: 50%}
    end
    
    Redis PubSub->>WebSocket: Message received
    WebSocket->>Client: Send update
    Client->>Client: Update progress bar
    
    par Score Calculation Complete
        Celery->>Redis PubSub: Publish completion
        Note over Celery,Redis PubSub: channel:result:{id}<br/>{status: 'completed', scores: {...}}
    end
    
    Redis PubSub->>WebSocket: Message received
    WebSocket->>Client: Send completion
    Client->>Client: Show results
```

**Примечание:** WebSocket функционал планируется для будущих версий для real-time обновлений прогресса обработки тестов.

## Резюме потоков данных

### Синхронные потоки
1. **Аутентификация** - немедленный ответ с JWT token
2. **Получение вопросов** - с кэшированием на двух уровнях
3. **Просмотр результатов** - прямой запрос к БД с проверкой прав

### Асинхронные потоки
1. **Расчет баллов** - через Celery с polling
2. **Генерация PDF** - через Celery с кэшированием
3. **Email уведомления** - фоновая задача без ожидания

### Критические точки производительности
1. **Перемешивание вопросов** - кэшируется в Redis
2. **Расчет баллов** - выполняется асинхронно
3. **Генерация PDF** - кэшируется на 24 часа
4. **Сессии пользователей** - кэшируются в Redis

### Точки отказоустойчивости
1. **Retry механизм** в Celery (3 попытки)
2. **Транзакции** в PostgreSQL
3. **Graceful degradation** при недоступности Redis
4. **Error boundaries** в React компонентах
