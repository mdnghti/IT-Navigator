# Схема Backend архитектуры IT Navigator

## Общая структура Backend

```mermaid
graph TB
    subgraph "FastAPI Application"
        FastAPI[FastAPI App]
        
        subgraph "API Layer"
            Router[API Router v1]
            
            subgraph "Endpoints"
                AuthEndpoints[Auth Endpoints]
                TestEndpoints[Test Endpoints]
                ResultEndpoints[Result Endpoints]
            end
        end
        
        subgraph "Business Logic"
            CRUD[CRUD Operations]
            Scoring[Scoring Engine]
            Security[Security Utils]
        end
        
        subgraph "Admin Panel"
            SQLAdmin[SQLAdmin]
            AdminAuth[Admin Auth]
            AdminViews[Admin Views]
        end
    end
    
    subgraph "Database Layer"
        SQLAlchemy[SQLAlchemy ORM]
        AsyncSession[Async Session]
        
        subgraph "Models"
            User[User Model]
            Specialty[Specialty Model]
            Test[Test Model]
            Question[Question Model]
            Answer[Answer Model]
            Result[TestResult Model]
        end
    end
    
    subgraph "Background Processing"
        Celery[Celery Worker]
        
        subgraph "Tasks"
            ScoringTask[Score Calculation]
            PDFTask[PDF Generation]
            EmailTask[Email Notifications]
        end
    end
    
    subgraph "External Services"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis)]
    end
    
    FastAPI --> Router
    Router --> AuthEndpoints
    Router --> TestEndpoints
    Router --> ResultEndpoints
    
    AuthEndpoints --> Security
    TestEndpoints --> CRUD
    ResultEndpoints --> CRUD
    
    CRUD --> Scoring
    Security --> CRUD
    
    FastAPI --> SQLAdmin
    SQLAdmin --> AdminAuth
    SQLAdmin --> AdminViews
    
    CRUD --> SQLAlchemy
    SQLAlchemy --> AsyncSession
    
    AsyncSession --> User
    AsyncSession --> Specialty
    AsyncSession --> Test
    AsyncSession --> Question
    AsyncSession --> Answer
    AsyncSession --> Result
    
    User --> PostgreSQL
    Specialty --> PostgreSQL
    Test --> PostgreSQL
    Question --> PostgreSQL
    Answer --> PostgreSQL
    Result --> PostgreSQL
    
    FastAPI --> Celery
    Celery --> ScoringTask
    Celery --> PDFTask
    Celery --> EmailTask
    
    Celery --> Redis
    AsyncSession --> PostgreSQL
```

## Структура директорий Backend

```
backend/
├── app/
│   ├── main.py                      # FastAPI app factory
│   │
│   ├── api/                         # API layer
│   │   ├── dependencies.py          # Dependency injection
│   │   └── v1/
│   │       ├── router.py            # Main router
│   │       └── endpoints/
│   │           ├── auth.py          # Auth endpoints
│   │           └── tests.py         # Test endpoints
│   │
│   ├── core/                        # Core configuration
│   │   ├── config.py                # Settings (Pydantic)
│   │   ├── security.py              # JWT & password hashing
│   │   ├── logging.py               # Logging setup
│   │   └── cache.py                 # Redis cache utils
│   │
│   ├── db/                          # Database layer
│   │   ├── base.py                  # SQLAlchemy Base
│   │   ├── session.py               # Async session factory
│   │   └── models/
│   │       ├── user.py              # User model
│   │       ├── specialty.py         # Specialty model
│   │       ├── test.py              # Test model
│   │       ├── question.py          # Question model
│   │       ├── answer.py            # Answer model
│   │       └── result.py            # TestResult model
│   │
│   ├── crud/                        # CRUD operations
│   │   ├── user.py                  # User CRUD
│   │   ├── test.py                  # Test CRUD
│   │   └── scoring.py               # Scoring logic
│   │
│   ├── schemas/                     # Pydantic schemas
│   │   ├── user.py                  # User schemas
│   │   └── test.py                  # Test schemas
│   │
│   ├── admin/                       # Admin panel
│   │   ├── auth.py                  # Admin authentication
│   │   └── views.py                 # SQLAdmin views
│   │
│   └── worker/                      # Celery worker
│       ├── celery_app.py            # Celery config
│       └── tasks.py                 # Background tasks
│
├── alembic/                         # Database migrations
│   ├── env.py                       # Alembic config
│   └── versions/                    # Migration files
│
├── scripts/                         # Utility scripts
│   ├── init_db.py                   # Database initialization
│   └── import_it_tests.py           # Import test data
│
├── tests/                           # Tests
│   ├── conftest.py                  # Test fixtures
│   ├── test_auth.py                 # Auth tests
│   ├── test_tests_api.py            # Test API tests
│   └── test_scoring.py              # Scoring tests
│
├── .env                             # Environment variables
├── alembic.ini                      # Alembic configuration
├── pyproject.toml                   # Python dependencies
└── Dockerfile                       # Docker configuration
```

## Database Models и связи

```mermaid
erDiagram
    User ||--o{ TestResult : "has many"
    Specialty ||--o{ Test : "has many"
    Specialty ||--o{ Question : "has many"
    Test ||--o{ Question : "has many"
    Question ||--o{ Answer : "has many"
    TestResult }o--|| User : "belongs to"
    TestResult }o--|| Test : "belongs to"
    
    User {
        int id PK
        string email UK
        string hashed_password
        string full_name
        boolean is_active
        boolean is_admin
        datetime created_at
        datetime updated_at
    }
    
    Specialty {
        int id PK
        string code UK "F1-F7"
        string name
        string description
        datetime created_at
    }
    
    Test {
        int id PK
        string test_type "general/specialized"
        int specialty_id FK
        string title
        string description
        int duration_minutes
        datetime created_at
    }
    
    Question {
        int id PK
        int test_id FK
        int specialty_id FK
        string text
        string question_type "single/multiple"
        int order_index
        datetime created_at
    }
    
    Answer {
        int id PK
        int question_id FK
        string text
        json weights "specialty_code: weight"
        int order_index
        datetime created_at
    }
    
    TestResult {
        int id PK
        int user_id FK
        int test_id FK
        json scores "specialty_code: score"
        json answers "question_id: answer_ids"
        datetime started_at
        datetime completed_at
        datetime created_at
    }
```

## API Endpoints

### Authentication Endpoints

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Auth Endpoint
    participant S as Security Utils
    participant DB as Database
    participant R as Redis

    Note over C,R: POST /api/v1/auth/register
    C->>A: Register request
    A->>S: Hash password
    S-->>A: Hashed password
    A->>DB: Create user
    DB-->>A: User created
    A->>S: Create JWT token
    S-->>A: JWT token
    A-->>C: {token, user}

    Note over C,R: POST /api/v1/auth/login
    C->>A: Login request
    A->>DB: Get user by email
    DB-->>A: User data
    A->>S: Verify password
    S-->>A: Password valid
    A->>S: Create JWT token
    S-->>A: JWT token
    A->>R: Cache session
    A-->>C: {token, user}

    Note over C,R: GET /api/v1/auth/me
    C->>A: Get current user
    A->>S: Verify JWT token
    S-->>A: User ID
    A->>DB: Get user by ID
    DB-->>A: User data
    A-->>C: User data
```

**Endpoints:**
- `POST /api/v1/auth/register` - Регистрация нового пользователя
- `POST /api/v1/auth/login` - Вход в систему
- `GET /api/v1/auth/me` - Получение текущего пользователя
- `POST /api/v1/auth/logout` - Выход из системы

### Test Endpoints

```mermaid
sequenceDiagram
    participant C as Client
    participant T as Test Endpoint
    participant CRUD as CRUD Layer
    participant DB as Database
    participant Cache as Redis Cache

    Note over C,Cache: GET /api/v1/tests/general/questions
    C->>T: Get questions
    T->>Cache: Check cache
    Cache-->>T: Cache miss
    T->>CRUD: Get questions
    CRUD->>DB: Query questions + answers
    DB-->>CRUD: Questions data
    CRUD->>CRUD: Shuffle questions & answers
    CRUD-->>T: Shuffled questions
    T->>Cache: Cache questions (5 min)
    T-->>C: Questions array

    Note over C,Cache: POST /api/v1/tests/general/submit
    C->>T: Submit answers
    T->>CRUD: Validate answers
    CRUD->>DB: Get answer weights
    DB-->>CRUD: Weights data
    CRUD->>CRUD: Calculate scores
    CRUD->>DB: Save result
    DB-->>CRUD: Result saved
    CRUD-->>T: Result ID
    T-->>C: {result_id, scores}
```

**Endpoints:**
- `GET /api/v1/tests/general/questions` - Получить вопросы общего теста
- `POST /api/v1/tests/general/submit` - Отправить ответы общего теста
- `GET /api/v1/tests/specialized/{code}/questions` - Получить вопросы специализированного теста
- `POST /api/v1/tests/specialized/{code}/submit` - Отправить ответы специализированного теста
- `GET /api/v1/tests/results/my` - Получить результаты текущего пользователя
- `GET /api/v1/tests/results/{id}` - Получить конкретный результат

## CRUD Operations

```mermaid
graph TB
    subgraph "User CRUD"
        CreateUser[Create User]
        GetUser[Get User]
        UpdateUser[Update User]
        DeleteUser[Delete User]
    end
    
    subgraph "Test CRUD"
        GetTest[Get Test]
        GetQuestions[Get Questions]
        ShuffleQuestions[Shuffle Questions]
        ValidateAnswers[Validate Answers]
    end
    
    subgraph "Result CRUD"
        CreateResult[Create Result]
        GetResult[Get Result]
        GetUserResults[Get User Results]
        CalculateScores[Calculate Scores]
    end
    
    subgraph "Database Operations"
        AsyncSession[Async Session]
        Transaction[Transaction Management]
        ErrorHandling[Error Handling]
    end
    
    CreateUser --> AsyncSession
    GetUser --> AsyncSession
    UpdateUser --> AsyncSession
    DeleteUser --> AsyncSession
    
    GetTest --> AsyncSession
    GetQuestions --> ShuffleQuestions
    ShuffleQuestions --> AsyncSession
    ValidateAnswers --> AsyncSession
    
    CreateResult --> CalculateScores
    CalculateScores --> AsyncSession
    GetResult --> AsyncSession
    GetUserResults --> AsyncSession
    
    AsyncSession --> Transaction
    Transaction --> ErrorHandling
```

**crud/test.py:**
```python
async def get_test_questions(
    db: AsyncSession,
    test_id: int,
    shuffle: bool = True
) -> List[Question]:
    """Get test questions with answers, optionally shuffled."""
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.answers))
        .where(Question.test_id == test_id)
        .order_by(Question.order_index)
    )
    questions = result.scalars().all()
    
    if shuffle:
        questions = list(questions)
        random.shuffle(questions)
        for question in questions:
            answers = list(question.answers)
            random.shuffle(answers)
            question.answers = answers
    
    return questions
```

**crud/scoring.py:**
```python
async def calculate_test_scores(
    db: AsyncSession,
    answers: Dict[int, List[int]]
) -> Dict[str, float]:
    """Calculate specialty scores based on answer weights."""
    scores = defaultdict(float)
    
    for question_id, answer_ids in answers.items():
        result = await db.execute(
            select(Answer)
            .where(Answer.id.in_(answer_ids))
        )
        selected_answers = result.scalars().all()
        
        for answer in selected_answers:
            for specialty_code, weight in answer.weights.items():
                scores[specialty_code] += weight
    
    # Normalize scores to 0-100 range
    max_score = max(scores.values()) if scores else 1
    normalized = {
        code: (score / max_score) * 100
        for code, score in scores.items()
    }
    
    return normalized
```

## Security Layer

```mermaid
graph TB
    subgraph "Authentication"
        JWTToken[JWT Token]
        TokenValidation[Token Validation]
        TokenRefresh[Token Refresh]
    end
    
    subgraph "Authorization"
        RoleCheck[Role Check]
        PermissionCheck[Permission Check]
        ResourceOwnership[Resource Ownership]
    end
    
    subgraph "Password Security"
        PasswordHash[Password Hashing - bcrypt]
        PasswordValidation[Password Validation]
        PasswordPolicy[Password Policy]
    end
    
    subgraph "Request Security"
        CORS[CORS Policy]
        RateLimiting[Rate Limiting]
        InputValidation[Input Validation]
    end
    
    JWTToken --> TokenValidation
    TokenValidation --> TokenRefresh
    
    TokenValidation --> RoleCheck
    RoleCheck --> PermissionCheck
    PermissionCheck --> ResourceOwnership
    
    PasswordHash --> PasswordValidation
    PasswordValidation --> PasswordPolicy
    
    CORS --> RateLimiting
    RateLimiting --> InputValidation
```

**core/security.py:**
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)
```

**api/dependencies.py:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await crud.user.get(db, id=user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify current user is admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

## Background Processing (Celery)

```mermaid
graph TB
    subgraph "Celery Worker"
        CeleryApp[Celery App]
        
        subgraph "Task Queue"
            TaskQueue[Redis Queue]
            TaskScheduler[Beat Scheduler]
        end
        
        subgraph "Tasks"
            ScoringTask[Score Calculation Task]
            CleanupTask[Cleanup Task]
        end
    end
    
    subgraph "Task Execution"
        TaskRetry[Retry Logic]
        TaskLogging[Task Logging]
        TaskMonitoring[Flower Monitoring]
    end
    
    CeleryApp --> TaskQueue
    CeleryApp --> TaskScheduler
    
    TaskQueue --> ScoringTask
    TaskQueue --> PDFTask
    TaskQueue --> EmailTask
    TaskScheduler --> CleanupTask
    
    ScoringTask --> TaskRetry
    PDFTask --> TaskRetry
    EmailTask --> TaskRetry
    
    TaskRetry --> TaskLogging
    TaskLogging --> TaskMonitoring
```

**worker/celery_app.py:**
```python
from celery import Celery

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)
```

**worker/tasks.py:**
```python
from .celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def calculate_test_scores(self, result_id: int):
    """Background task to calculate test scores."""
    try:
        # Get database session
        db = SessionLocal()
        
        # Get test result
        result = db.query(TestResult).get(result_id)
        
        # Calculate scores
        scores = calculate_scores(db, result.answers)
        
        # Update result
        result.scores = scores
        result.completed_at = datetime.utcnow()
        db.commit()
        
        # Send notification
        send_result_notification.delay(result_id)
        
        return {"result_id": result_id, "scores": scores}
        
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    finally:
        db.close()

@celery_app.task
def generate_result_pdf(result_id: int):
    """Generate PDF report for test result."""
    # PDF generation logic
    pass

@celery_app.task
def send_result_notification(result_id: int):
    """Send email notification about test completion."""
    # Email sending logic
    pass

@celery_app.task
def cleanup_old_results():
    """Periodic task to cleanup old test results."""
    # Cleanup logic
    pass
```

## Admin Panel (SQLAdmin)

```mermaid
graph TB
    subgraph "SQLAdmin Interface"
        AdminPanel[Admin Panel]
        
        subgraph "Model Views"
            UserView[User View]
            SpecialtyView[Specialty View]
            TestView[Test View]
            QuestionView[Question View]
            AnswerView[Answer View]
            ResultView[Result View]
        end
        
        subgraph "CRUD Operations"
            Create[Create]
            Read[Read]
            Update[Update]
            Delete[Delete]
        end
    end
    
    subgraph "Authentication"
        AdminAuth[Admin Authentication]
        SessionManagement[Session Management]
    end
    
    AdminPanel --> AdminAuth
    AdminAuth --> SessionManagement
    
    SessionManagement --> UserView
    SessionManagement --> SpecialtyView
    SessionManagement --> TestView
    SessionManagement --> QuestionView
    SessionManagement --> AnswerView
    SessionManagement --> ResultView
    
    UserView --> Create
    UserView --> Read
    UserView --> Update
    UserView --> Delete
```

**admin/views.py:**
```python
from sqladmin import ModelView

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.full_name, User.is_active, User.is_admin]
    column_searchable_list = [User.email, User.full_name]
    column_sortable_list = [User.id, User.email, User.created_at]
    column_default_sort = [(User.created_at, True)]
    
    form_excluded_columns = [User.hashed_password]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class TestAdmin(ModelView, model=Test):
    column_list = [Test.id, Test.test_type, Test.title, Test.specialty]
    column_searchable_list = [Test.title, Test.description]
    column_sortable_list = [Test.id, Test.test_type, Test.created_at]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class QuestionAdmin(ModelView, model=Question):
    column_list = [Question.id, Question.text, Question.test, Question.specialty]
    column_searchable_list = [Question.text]
    column_sortable_list = [Question.id, Question.order_index]
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
```

## Caching Strategy

```mermaid
graph TB
    subgraph "Cache Layers"
        RedisCache[Redis Cache]
        
        subgraph "Cached Data"
            TestQuestions[Test Questions - 5 min]
            UserSessions[User Sessions - 24 hours]
            SpecialtyData[Specialty Data - 1 hour]
            ResultCache[Result Cache - 10 min]
        end
    end
    
    subgraph "Cache Operations"
        CacheGet[Get from Cache]
        CacheSet[Set to Cache]
        CacheInvalidate[Invalidate Cache]
        CacheWarmup[Cache Warmup]
    end
    
    RedisCache --> TestQuestions
    RedisCache --> UserSessions
    RedisCache --> SpecialtyData
    RedisCache --> ResultCache
    
    CacheGet --> CacheSet
    CacheSet --> CacheInvalidate
    CacheInvalidate --> CacheWarmup
```

**core/cache.py:**
```python
import redis
from functools import wraps

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache_result(key_prefix: str, ttl: int = 300):
    """Decorator to cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{args}:{kwargs}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator
```

## Logging и Monitoring

```mermaid
graph TB
    subgraph "Logging"
        AppLogger[Application Logger]
        AccessLogger[Access Logger]
        ErrorLogger[Error Logger]
        AuditLogger[Audit Logger]
    end
    
    subgraph "Log Destinations"
        Console[Console Output]
        FileLog[Log Files]
        Sentry[Sentry Error Tracking]
    end
    
    subgraph "Monitoring"
        Prometheus[Prometheus Metrics]
        HealthCheck[Health Check Endpoint]
        Flower[Flower - Celery Monitor]
    end
    
    AppLogger --> Console
    AppLogger --> FileLog
    ErrorLogger --> Sentry
    AuditLogger --> FileLog
    
    Prometheus --> HealthCheck
    Flower --> Prometheus
```

**core/logging.py:**
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure application logging."""
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

## Database Migrations (Alembic)

```mermaid
graph LR
    subgraph "Migration Workflow"
        ModelChange[Model Change]
        GenerateMigration[alembic revision --autogenerate]
        ReviewMigration[Review Migration]
        ApplyMigration[alembic upgrade head]
        Rollback[alembic downgrade -1]
    end
    
    ModelChange --> GenerateMigration
    GenerateMigration --> ReviewMigration
    ReviewMigration --> ApplyMigration
    ApplyMigration --> Rollback
```

**Commands:**
```bash
# Generate migration
alembic revision --autogenerate -m "add user table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

## Testing Strategy

```mermaid
graph TB
    subgraph "Unit Tests"
        CRUDTests[CRUD Tests]
        ScoringTests[Scoring Tests]
        SecurityTests[Security Tests]
    end
    
    subgraph "Integration Tests"
        APITests[API Endpoint Tests]
        DatabaseTests[Database Tests]
        CeleryTests[Celery Task Tests]
    end
    
    subgraph "Test Fixtures"
        TestDB[Test Database]
        TestData[Test Data]
        MockServices[Mock Services]
    end
    
    CRUDTests --> TestDB
    ScoringTests --> TestData
    SecurityTests --> MockServices
    
    APITests --> TestDB
    DatabaseTests --> TestDB
    CeleryTests --> MockServices
```

**tests/conftest.py:**
```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost/test_db"
    )
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def test_user():
    """Create test user."""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
```

## Performance Optimization

```mermaid
graph TB
    subgraph "Database Optimization"
        Indexing[Database Indexes]
        QueryOptimization[Query Optimization]
        ConnectionPooling[Connection Pooling]
    end
    
    subgraph "Caching"
        RedisCache[Redis Cache]
        QueryCache[Query Result Cache]
        SessionCache[Session Cache]
    end
    
    subgraph "Async Processing"
        AsyncIO[Async I/O]
        BackgroundTasks[Background Tasks]
        CeleryWorkers[Celery Workers]
    end
    
    Indexing --> QueryOptimization
    QueryOptimization --> ConnectionPooling
    
    RedisCache --> QueryCache
    QueryCache --> SessionCache
    
    AsyncIO --> BackgroundTasks
    BackgroundTasks --> CeleryWorkers
```

**Optimization techniques:**
- Database indexes on frequently queried columns
- Async SQLAlchemy for non-blocking I/O
- Redis caching for expensive queries
- Connection pooling for database connections
- Celery for long-running tasks
- Query result pagination
- Lazy loading with selectinload/joinedload
