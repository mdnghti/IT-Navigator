# План реализации: 5 блоков
## Профориентационная платформа (FastAPI + PostgreSQL + React + Celery)

---

## Блок 1 — Фундамент

**Цель:** рабочий бэкенд с БД, авторизацией и админкой для конструктора тестов.

### 1.1 Структура проекта и инфраструктура качества

```
IT-Navigator/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   ├── core/          # config.py, security.py
│   │   ├── db/
│   │   │   ├── models/
│   │   │   └── session.py
│   │   ├── schemas/
│   │   ├── crud/
│   │   ├── admin/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
├── nginx/
│   └── nginx.conf
└── docker-compose.yml
```

**pyproject.toml:**
```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**`.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, sqlalchemy[mypy]]
```

---

### 1.2 Docker Compose — БД

```yaml
# docker-compose.yml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    restart: unless-stopped
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

---

### 1.3 Модели SQLAlchemy (async) + Alembic

```python
# db/base.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

```python
# db/models/user.py
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    results: Mapped[list["TestResult"]] = relationship(back_populates="user")
```

```python
# db/models/specialty.py
class Specialty(Base):
    __tablename__ = "specialties"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True)  # F1..F7
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    questions: Mapped[list["Question"]] = relationship(back_populates="specialty")
```

```python
# db/models/test.py
class TestType(PyEnum):
    GENERAL = "general"
    SPECIALIZED = "specialized"

class Test(Base):
    __tablename__ = "tests"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    test_type: Mapped[TestType] = mapped_column(Enum(TestType))
    specialty_id: Mapped[int | None] = mapped_column(ForeignKey("specialties.id"))
    is_active: Mapped[bool] = mapped_column(default=True)
    questions: Mapped[list["Question"]] = relationship(back_populates="test", cascade="all, delete-orphan")
```

```python
# db/models/question.py
class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))
    specialty_id: Mapped[int | None] = mapped_column(ForeignKey("specialties.id"))
    text: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)
    test: Mapped["Test"] = relationship(back_populates="questions")
    specialty: Mapped["Specialty | None"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question", cascade="all, delete-orphan")
```

```python
# db/models/answer.py
class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column(String(1000))
    weight: Mapped[int] = mapped_column(Integer, default=0)
    # 10 = верный, 5 = близкий, 0 = неверный
    question: Mapped["Question"] = relationship(back_populates="answers")
```

```python
# db/models/result.py
class TestResult(Base):
    __tablename__ = "test_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))
    payload: Mapped[dict] = mapped_column(JSON)  # сырые ответы
    scores: Mapped[dict] = mapped_column(JSON)   # {specialty_code: percentage}
    completed_at: Mapped[datetime] = mapped_column(default=func.now())
    user: Mapped["User"] = relationship(back_populates="results")
```

**Инициализация Alembic:**
```bash
alembic init alembic
alembic revision --autogenerate -m "initial_tables"
alembic upgrade head
```

---

### 1.4 FastAPI — Auth эндпоинты

```python
# core/security.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: str | int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(subject), "exp": expire}, settings.SECRET_KEY)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

```python
# api/v1/endpoints/auth.py
@router.post("/register", response_model=UserRead, status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    if await user_crud.get_by_email(db, user_in.email):
        raise HTTPException(400, "Email already registered")
    return await user_crud.create(db, user_in)

@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_email(db, form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}
```

---

### 1.5 SQLAdmin — Конструктор тестов

```python
# admin/views.py
class TestAdmin(ModelView, model=Test):
    column_list = [Test.id, Test.title, Test.test_type, Test.specialty, Test.is_active]
    column_filters = [Test.test_type, Test.is_active]

class QuestionAdmin(ModelView, model=Question):
    column_list = [Question.id, Question.text, Question.test, Question.specialty]

class AnswerAdmin(ModelView, model=Answer):
    column_list = [Answer.id, Answer.text, Answer.weight, Answer.question]

class SpecialtyAdmin(ModelView, model=Specialty):
    column_list = [Specialty.code, Specialty.name]
```

```python
# main.py
def create_app() -> FastAPI:
    app = FastAPI(title="Career Platform API")
    admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key=settings.SECRET_KEY))
    for view in [SpecialtyAdmin, TestAdmin, QuestionAdmin, AnswerAdmin, UserAdmin]:
        admin.add_view(view)
    return app
```

**Зависимости Блока 1:**
```
fastapi, uvicorn[standard], sqlalchemy[asyncio], asyncpg,
alembic, sqladmin, python-jose[cryptography], passlib[bcrypt],
python-multipart, pydantic-settings
```

**Результат блока:** рабочий бэкенд на :8000, PostgreSQL в Docker, JWT-авторизация, SQLAdmin на /admin — преподаватель может создавать тесты, вопросы и назначать веса ответам.

---

## Блок 2 — Ядро тестирования

**Цель:** полный цикл прохождения теста через API — от получения вопросов до итоговой таблицы специальностей.

### 2.1 Схемы запросов/ответов

```python
# schemas/test.py
class AnswerRead(BaseModel):
    id: int
    text: str
    model_config = ConfigDict(from_attributes=True)
    # weight намеренно не отдаём клиенту

class QuestionRead(BaseModel):
    id: int
    text: str
    answers: list[AnswerRead]
    model_config = ConfigDict(from_attributes=True)

class AnswerSubmit(BaseModel):
    question_id: int
    answer_id: int

class TestSubmitRequest(BaseModel):
    answers: list[AnswerSubmit]

class SpecialtyResult(BaseModel):
    specialty_code: str
    specialty_name: str
    score: int
    max_score: int
    percentage: float

class TestResultResponse(BaseModel):
    results: list[SpecialtyResult]        # отсортировано по percentage DESC
    recommended_specialty: SpecialtyResult | None
    result_id: int
```

---

### 2.2 CRUD — получение вопросов

```python
# crud/test.py
async def get_general_test_questions(db: AsyncSession) -> list[Question]:
    stmt = (
        select(Question)
        .join(Test)
        .where(Test.test_type == TestType.GENERAL, Test.is_active == True)
        .options(selectinload(Question.answers), selectinload(Question.specialty))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_specialized_test_questions(db: AsyncSession, specialty_code: str) -> list[Question]:
    stmt = (
        select(Question)
        .join(Test)
        .join(Specialty, Test.specialty_id == Specialty.id)
        .where(
            Test.test_type == TestType.SPECIALIZED,
            Test.is_active == True,
            Specialty.code == specialty_code,
        )
        .options(selectinload(Question.answers))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
```

---

### 2.3 Алгоритм подсчёта баллов

```python
# crud/scoring.py
from collections import defaultdict

async def get_max_weight_for_question(db: AsyncSession, question_id: int) -> int:
    stmt = select(func.max(Answer.weight)).where(Answer.question_id == question_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() or 0

async def calculate_result(
    db: AsyncSession,
    user_id: int,
    test_id: int,
    submissions: list[AnswerSubmit],
) -> TestResultResponse:
    specialty_scores: dict[str, int] = defaultdict(int)
    specialty_max: dict[str, int] = defaultdict(int)
    specialty_names: dict[str, str] = {}

    for sub in submissions:
        answer = await db.get(Answer, sub.answer_id)
        question = await db.get(Question, sub.question_id)
        if not answer or not question or not question.specialty_id:
            continue

        specialty = await db.get(Specialty, question.specialty_id)
        if not specialty:
            continue

        code = specialty.code
        specialty_names[code] = specialty.name
        specialty_scores[code] += answer.weight
        specialty_max[code] += await get_max_weight_for_question(db, question.id)

    results = [
        SpecialtyResult(
            specialty_code=code,
            specialty_name=specialty_names[code],
            score=specialty_scores[code],
            max_score=specialty_max[code],
            percentage=round(specialty_scores[code] / specialty_max[code] * 100, 1)
            if specialty_max[code] else 0.0,
        )
        for code in specialty_scores
    ]
    results.sort(key=lambda r: r.percentage, reverse=True)

    # Сохраняем результат в БД
    test_result = TestResult(
        user_id=user_id,
        test_id=test_id,
        payload={"answers": [s.model_dump() for s in submissions]},
        scores={r.specialty_code: r.percentage for r in results},
    )
    db.add(test_result)
    await db.commit()
    await db.refresh(test_result)

    return TestResultResponse(
        results=results,
        recommended_specialty=results[0] if results else None,
        result_id=test_result.id,
    )
```

---

### 2.4 API эндпоинты тестирования

```python
# api/v1/endpoints/tests.py
import random

@router.get("/general/questions", response_model=list[QuestionRead])
async def get_general_questions(db: AsyncSession = Depends(get_db)):
    questions = await get_general_test_questions(db)
    random.shuffle(questions)
    for q in questions:
        random.shuffle(q.answers)
    return questions

@router.get("/specialized/{specialty_code}/questions", response_model=list[QuestionRead])
async def get_specialized_questions(specialty_code: str, db: AsyncSession = Depends(get_db)):
    questions = await get_specialized_test_questions(db, specialty_code)
    random.shuffle(questions)
    for q in questions:
        random.shuffle(q.answers)
    return questions

@router.post("/general/submit", response_model=TestResultResponse)
async def submit_general_test(
    body: TestSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    general_test = await get_active_general_test(db)
    return await calculate_result(db, current_user.id, general_test.id, body.answers)

@router.post("/specialized/{specialty_code}/submit", response_model=TestResultResponse)
async def submit_specialized_test(
    specialty_code: str,
    body: TestSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    test = await get_active_specialized_test(db, specialty_code)
    return await calculate_result(db, current_user.id, test.id, body.answers)

@router.get("/results/my", response_model=list[TestResultRead])
async def get_my_results(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_results(db, current_user.id)
```

**Результат блока:** через Swagger (/docs) можно пройти полный цикл — получить вопросы, отправить ответы, получить таблицу F1–F7 с процентами и рекомендацию.

---

## Блок 3 — Фронтенд

**Цель:** полный user flow в браузере — регистрация → общий тест → результаты → специализированный тест.

### 3.1 Инициализация и стек

```bash
# Next.js 14, App Router
npx create-next-app@latest frontend --typescript --tailwind --eslint --app
cd frontend
npm install axios react-query @tanstack/react-query zustand
```

**Структура:**
```
frontend/src/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── test/
│   │   ├── general/page.tsx
│   │   └── specialized/[code]/page.tsx
│   ├── results/
│   │   └── [id]/page.tsx
│   └── dashboard/page.tsx
├── components/
│   ├── ui/               # Button, Card, Progress и др.
│   ├── test/
│   │   ├── QuestionCard.tsx
│   │   ├── AnswerOption.tsx
│   │   └── TestProgress.tsx
│   └── results/
│       ├── SpecialtyTable.tsx
│       └── RecommendationCard.tsx
├── lib/
│   ├── api.ts            # axios instance
│   └── auth.ts           # токен хелперы
└── store/
    └── testStore.ts      # zustand: ответы пользователя
```

---

### 3.2 API клиент

```typescript
// lib/api.ts
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// API функции
export const authApi = {
  register: (data: RegisterPayload) => api.post("/auth/register", data),
  login: (data: LoginPayload) =>
    api.post<{ access_token: string }>("/auth/login", data, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    }),
};

export const testApi = {
  getGeneralQuestions: () => api.get<Question[]>("/tests/general/questions"),
  submitGeneral: (answers: AnswerSubmit[]) =>
    api.post<TestResultResponse>("/tests/general/submit", { answers }),
  getSpecializedQuestions: (code: string) =>
    api.get<Question[]>(`/tests/specialized/${code}/questions`),
  submitSpecialized: (code: string, answers: AnswerSubmit[]) =>
    api.post<TestResultResponse>(`/tests/specialized/${code}/submit`, { answers }),
  getMyResults: () => api.get<TestResult[]>("/tests/results/my"),
};
```

---

### 3.3 Zustand store — состояние теста

```typescript
// store/testStore.ts
import { create } from "zustand";

interface TestState {
  answers: Record<number, number>; // question_id -> answer_id
  currentIndex: number;
  setAnswer: (questionId: number, answerId: number) => void;
  nextQuestion: () => void;
  prevQuestion: () => void;
  reset: () => void;
}

export const useTestStore = create<TestState>((set) => ({
  answers: {},
  currentIndex: 0,
  setAnswer: (questionId, answerId) =>
    set((s) => ({ answers: { ...s.answers, [questionId]: answerId } })),
  nextQuestion: () => set((s) => ({ currentIndex: s.currentIndex + 1 })),
  prevQuestion: () => set((s) => ({ currentIndex: Math.max(0, s.currentIndex - 1) })),
  reset: () => set({ answers: {}, currentIndex: 0 }),
}));
```

---

### 3.4 Ключевые компоненты

```tsx
// components/test/QuestionCard.tsx
export function QuestionCard({ question, totalCount, currentIndex }: Props) {
  const { answers, setAnswer } = useTestStore();
  const selected = answers[question.id];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>Вопрос {currentIndex + 1} из {totalCount}</span>
        <Progress value={((currentIndex + 1) / totalCount) * 100} className="w-48" />
      </div>
      <h2 className="text-xl font-semibold">{question.text}</h2>
      <div className="flex flex-col gap-3">
        {question.answers.map((answer) => (
          <AnswerOption
            key={answer.id}
            answer={answer}
            selected={selected === answer.id}
            onSelect={() => setAnswer(question.id, answer.id)}
          />
        ))}
      </div>
    </div>
  );
}
```

```tsx
// components/results/SpecialtyTable.tsx
export function SpecialtyTable({ results }: { results: SpecialtyResult[] }) {
  return (
    <div className="flex flex-col gap-3">
      {results.map((r) => (
        <div key={r.specialty_code} className="flex items-center gap-4">
          <span className="w-8 font-bold text-blue-600">{r.specialty_code}</span>
          <span className="w-48 truncate text-sm">{r.specialty_name}</span>
          <div className="flex-1">
            <div className="h-3 rounded-full bg-gray-100">
              <div
                className="h-3 rounded-full bg-blue-500 transition-all duration-700"
                style={{ width: `${r.percentage}%` }}
              />
            </div>
          </div>
          <span className="w-14 text-right font-semibold">{r.percentage}%</span>
        </div>
      ))}
    </div>
  );
}
```

---

### 3.5 CORS на бэкенде + Nginx роутинг

```python
# backend: main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

```nginx
# nginx/nginx.conf
server {
    listen 80;

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**docker-compose дополнение:**
```yaml
  frontend:
    build: ./frontend
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost/api/v1
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend
```

**Результат блока:** полный UI в браузере — регистрация, прохождение общего теста с прогресс-баром, страница результатов с таблицей F1–F7 и кнопкой перехода к специализированному тесту.

---

## Блок 4 — Фоновые задачи и аналитика

**Цель:** вынести тяжёлые операции в Celery, добавить кэширование и историю результатов пользователя.

### 4.1 Redis + Celery в docker-compose

```yaml
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  celery_worker:
    build: ./backend
    command: celery -A app.worker.celery_app worker -Q scoring,reports --loglevel=info --concurrency=4
    restart: unless-stopped
    env_file: .env
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy

  flower:
    image: mher/flower
    restart: unless-stopped
    command: celery flower --broker=redis://redis:6379/0
    ports:
      - "5555:5555"
    depends_on:
      - redis
```

---

### 4.2 Celery приложение и задачи

```python
# worker/celery_app.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "career_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.task_routes = {
    "app.worker.tasks.run_scoring": {"queue": "scoring"},
    "app.worker.tasks.generate_pdf_report": {"queue": "reports"},
}
celery_app.conf.task_serializer = "json"
celery_app.conf.result_expires = 3600
```

```python
# worker/tasks.py
from app.worker.celery_app import celery_app
from app.db.session import SyncSessionLocal  # синхронная сессия для Celery
from app.crud.scoring import calculate_result_sync

@celery_app.task(bind=True, max_retries=3, name="app.worker.tasks.run_scoring")
def run_scoring(self, user_id: int, test_id: int, answers: list[dict]):
    """
    Используется для сложных сценариев или когда нужен PDF.
    Синхронный подсчёт в воркере, результат пишется в БД.
    """
    try:
        with SyncSessionLocal() as db:
            result = calculate_result_sync(db, user_id, test_id, answers)
            return {"result_id": result.id, "scores": result.scores}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)

@celery_app.task(bind=True, name="app.worker.tasks.generate_pdf_report")
def generate_pdf_report(self, result_id: int):
    """Генерация PDF-отчёта по результатам теста."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    # ... генерация PDF и сохранение в /media/reports/
    return {"path": f"/media/reports/result_{result_id}.pdf"}
```

---

### 4.3 Async submit с polling статуса

```python
# schemas/task.py
class TaskStatus(BaseModel):
    task_id: str
    status: str           # PENDING | STARTED | SUCCESS | FAILURE
    result: dict | None

# api/v1/endpoints/tests.py — async вариант сабмита
@router.post("/general/submit/async", response_model=TaskStatus)
async def submit_general_test_async(
    body: TestSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    general_test = await get_active_general_test(db)
    task = run_scoring.delay(
        user_id=current_user.id,
        test_id=general_test.id,
        answers=[a.model_dump() for a in body.answers],
    )
    return TaskStatus(task_id=task.id, status="PENDING", result=None)

@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    return TaskStatus(
        task_id=task_id,
        status=result.status,
        result=result.result if result.ready() else None,
    )
```

---

### 4.4 Кэширование вопросов через Redis

```python
# core/cache.py
import json
import redis.asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_cached_questions(key: str) -> list | None:
    data = await redis_client.get(key)
    return json.loads(data) if data else None

async def set_cached_questions(key: str, data: list, ttl: int = 300) -> None:
    await redis_client.setex(key, ttl, json.dumps(data))

# crud/test.py — с кешем
async def get_general_test_questions_cached(db: AsyncSession) -> list[Question]:
    cache_key = "questions:general"
    cached = await get_cached_questions(cache_key)
    if cached:
        return cached  # возвращаем из Redis

    questions = await get_general_test_questions(db)
    serialized = [QuestionRead.model_validate(q).model_dump() for q in questions]
    await set_cached_questions(cache_key, serialized, ttl=600)
    return questions
```

---

### 4.5 Дашборд истории результатов (фронтенд)

```tsx
// app/dashboard/page.tsx
export default async function DashboardPage() {
  const { data: results } = useQuery({
    queryKey: ["my-results"],
    queryFn: () => testApi.getMyResults().then((r) => r.data),
  });

  return (
    <div className="flex flex-col gap-6 p-8">
      <h1 className="text-2xl font-bold">Мои результаты</h1>
      {results?.map((result) => (
        <ResultCard key={result.id} result={result} />
      ))}
    </div>
  );
}

// components/results/ResultCard.tsx
function ResultCard({ result }: { result: TestResult }) {
  const top = Object.entries(result.scores)
    .sort(([, a], [, b]) => b - a)[0];

  return (
    <div className="rounded-xl border p-5 flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-500">{formatDate(result.completed_at)}</p>
        <p className="font-semibold">Лидер: {top[0]} — {top[1]}%</p>
      </div>
      <Link href={`/results/${result.id}`}>
        <Button variant="outline">Подробнее</Button>
      </Link>
    </div>
  );
}
```

**Результат блока:** вопросы кешируются (Redis), тяжёлые расчёты в Celery-воркере, мониторинг задач через Flower на :5555, пользователь видит историю всех пройденных тестов.

---

## Блок 5 — Стабилизация и деплой

**Цель:** покрытие тестами, production-конфиг Docker, CI/CD, логирование.

### 5.1 Pytest — полное покрытие

```python
# tests/conftest.py
@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(db_session):
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

```python
# tests/test_auth.py
async def test_register_success(client): ...
async def test_register_duplicate_email(client): ...
async def test_login_success(client): ...
async def test_login_wrong_password(client): ...
async def test_protected_endpoint_no_token(client): ...
async def test_protected_endpoint_valid_token(client): ...
```

```python
# tests/test_scoring.py
async def test_full_score(db_session, seeded_questions):
    """Все правильные ответы -> 100%"""
    answers = [AnswerSubmit(question_id=q.id, answer_id=best_answer(q)) for q in seeded_questions]
    result = await calculate_result(db_session, user_id=1, test_id=1, submissions=answers)
    assert all(r.percentage == 100.0 for r in result.results)

async def test_zero_score(db_session, seeded_questions):
    """Все нулевые ответы -> 0%"""
    answers = [AnswerSubmit(question_id=q.id, answer_id=zero_answer(q)) for q in seeded_questions]
    result = await calculate_result(db_session, user_id=1, test_id=1, submissions=answers)
    assert all(r.percentage == 0.0 for r in result.results)

async def test_recommended_is_top(db_session, seeded_questions):
    """recommended_specialty всегда максимальный"""
    result = await calculate_result(db_session, user_id=1, test_id=1, submissions=mixed_answers)
    assert result.recommended_specialty.percentage == max(r.percentage for r in result.results)

async def test_sorting_desc(db_session, seeded_questions):
    """Результаты отсортированы по убыванию"""
    result = await calculate_result(...)
    percentages = [r.percentage for r in result.results]
    assert percentages == sorted(percentages, reverse=True)
```

```python
# tests/test_tests_api.py
async def test_get_general_questions_shuffled(client, auth_headers, seeded_general_test):
    r1 = await client.get("/api/v1/tests/general/questions", headers=auth_headers)
    r2 = await client.get("/api/v1/tests/general/questions", headers=auth_headers)
    # Порядок вопросов должен отличаться хотя бы иногда
    assert r1.status_code == 200
    assert len(r1.json()) > 0

async def test_submit_saves_to_db(client, auth_headers, db_session, seeded_general_test):
    questions = (await client.get("/api/v1/tests/general/questions", headers=auth_headers)).json()
    answers = [{"question_id": q["id"], "answer_id": q["answers"][0]["id"]} for q in questions]
    r = await client.post("/api/v1/tests/general/submit", json={"answers": answers}, headers=auth_headers)
    assert r.status_code == 200
    assert "result_id" in r.json()
    assert "results" in r.json()
```

---

### 5.2 Production docker-compose

```yaml
# docker-compose.prod.yml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    restart: always
    env_file: .env.prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # ports НЕТ — только внутренняя сеть
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always
    env_file: .env.prod
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod    # next build + next start
    restart: always
    env_file: .env.prod

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: celery -A app.worker.celery_app worker -Q scoring,reports --loglevel=warning --concurrency=4
    restart: always
    env_file: .env.prod
    depends_on:
      - redis
      - db

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/conf.d/default.conf
      - ./nginx/ssl:/etc/nginx/ssl   # SSL сертификаты
      - ./media:/var/www/media       # статика
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
```

---

### 5.3 CI/CD (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        run: pip install -e ".[dev]"
        working-directory: backend

      - name: Lint (Ruff)
        run: ruff check .
        working-directory: backend

      - name: Type check (Mypy)
        run: mypy app
        working-directory: backend

      - name: Run tests
        run: pytest --cov=app --cov-report=xml
        working-directory: backend
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost/test_db
          SECRET_KEY: ci-secret-key-not-for-production
          REDIS_URL: redis://localhost:6379/0

      - name: Upload coverage
        uses: codecov/codecov-action@v4

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - run: npm ci
        working-directory: frontend
      - run: npm run lint
        working-directory: frontend
      - run: npm run build
        working-directory: frontend
```

---

### 5.4 Логирование

```python
# core/logging.py
import logging
import sys
from app.core.config import settings

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log") if not settings.DEBUG else logging.NullHandler(),
        ],
    )

logger = logging.getLogger("career_platform")

# Использование в эндпоинтах:
# logger.info("User %s submitted general test", current_user.id)
# logger.error("Scoring failed for user %s: %s", user_id, exc)
```

---

## Сводная таблица блоков

| Блок | Фокус | Ключевые артефакты | Проверяемый результат |
|------|-------|--------------------|-----------------------|
| **1** | Фундамент | docker-compose (db), модели, Alembic, FastAPI auth, SQLAdmin | Бэкенд на :8000, админка на /admin, можно создавать тесты |
| **2** | Ядро тестирования | scoring алгоритм, API вопросов и сабмита, TestResult в БД | Полный цикл теста через Swagger /docs |
| **3** | Фронтенд | Next.js, zustand, axios, Nginx роутинг | Полный UI flow в браузере |
| **4** | Фоновые задачи | Redis, Celery, polling, кэш вопросов, история | Flower :5555, результаты из кеша, dashboard |
| **5** | Стабилизация | Pytest suite, GitHub Actions CI, prod compose, логирование | Все тесты зелёные, прод-деплой одной командой |

## Зависимости по блокам

```
Блок 1: fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic,
         sqladmin, python-jose, passlib[bcrypt], pydantic-settings

Блок 2: (всё из блока 1)

Блок 3: next, react, axios, @tanstack/react-query, zustand, tailwindcss

Блок 4: celery[redis], redis, reportlab (PDF)

Блок 5: pytest, pytest-asyncio, httpx, pytest-cov
```
