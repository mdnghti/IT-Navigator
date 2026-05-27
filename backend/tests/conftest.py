"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


# Test database URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    settings.POSTGRES_DB, f"{settings.POSTGRES_DB}_test"
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    app = create_app()

    # Override database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> dict:
    """Create test user."""
    from app.crud.user import create_user
    from app.schemas.user import UserCreate

    user_data = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User",
    )

    user = await create_user(db_session, user_data)
    await db_session.commit()

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "password": "testpassword123",
    }


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: dict) -> dict:
    """Get authentication headers for test user."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_specialty(db_session: AsyncSession):
    """Create test specialty."""
    from app.db.models.specialty import Specialty

    specialty = Specialty(
        code="F1",
        name="Программирование",
        description="Разработка программного обеспечения",
    )
    db_session.add(specialty)
    await db_session.commit()
    await db_session.refresh(specialty)

    return specialty


@pytest_asyncio.fixture
async def test_general_test(db_session: AsyncSession, test_specialty):
    """Create test general test with questions."""
    from app.db.models.answer import Answer
    from app.db.models.question import Question
    from app.db.models.test import Test, TestType

    # Create test
    test = Test(
        title="Общий тест",
        description="Тестовый общий тест",
        test_type=TestType.GENERAL,
        is_active=True,
    )
    db_session.add(test)
    await db_session.flush()

    # Create questions
    for i in range(3):
        question = Question(
            test_id=test.id,
            specialty_id=test_specialty.id,
            text=f"Вопрос {i + 1}",
            order=i,
        )
        db_session.add(question)
        await db_session.flush()

        # Create answers
        for j in range(3):
            answer = Answer(
                question_id=question.id,
                text=f"Ответ {j + 1}",
                weight=10 if j == 0 else (5 if j == 1 else 0),
            )
            db_session.add(answer)

    await db_session.commit()
    await db_session.refresh(test)

    return test
