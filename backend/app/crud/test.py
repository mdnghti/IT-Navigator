from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.cache import get_cached_questions, set_cached_questions
from app.db.models.question import Question
from app.db.models.test import Test, TestType
from app.schemas.test import QuestionRead


async def get_general_test_questions(db: AsyncSession) -> list[Question]:
    """Get all questions for general test with caching."""
    cache_key = "questions:general"

    # Try to get from cache
    cached = await get_cached_questions(cache_key)
    if cached:
        # Return cached data (note: these are dicts, not ORM objects)
        # For now, we'll skip cache and always fetch fresh for ORM objects
        pass

    stmt = (
        select(Question)
        .join(Test)
        .where(Test.test_type == TestType.GENERAL, Test.is_active == True)  # noqa: E712
        .options(selectinload(Question.answers), selectinload(Question.specialty))
    )
    result = await db.execute(stmt)
    questions = list(result.scalars().all())

    # Cache the serialized questions
    try:
        serialized = [QuestionRead.model_validate(q).model_dump() for q in questions]
        await set_cached_questions(cache_key, serialized, ttl=600)
    except Exception:
        pass  # Don't fail if caching fails

    return questions


async def get_specialized_test_questions(
    db: AsyncSession, specialty_code: str
) -> list[Question]:
    """Get all questions for specialized test by specialty code with caching."""
    from app.db.models.specialty import Specialty

    cache_key = f"questions:specialized:{specialty_code}"

    # Try to get from cache
    cached = await get_cached_questions(cache_key)
    if cached:
        # Return cached data (note: these are dicts, not ORM objects)
        # For now, we'll skip cache and always fetch fresh for ORM objects
        pass

    stmt = (
        select(Question)
        .join(Test)
        .join(Specialty, Test.specialty_id == Specialty.id)
        .where(
            Test.test_type == TestType.SPECIALIZED,
            Test.is_active == True,  # noqa: E712
            Specialty.code == specialty_code,
        )
        .options(selectinload(Question.answers))
    )
    result = await db.execute(stmt)
    questions = list(result.scalars().all())

    # Cache the serialized questions
    try:
        serialized = [QuestionRead.model_validate(q).model_dump() for q in questions]
        await set_cached_questions(cache_key, serialized, ttl=600)
    except Exception:
        pass  # Don't fail if caching fails

    return questions


async def get_active_general_test(db: AsyncSession) -> Test | None:
    """Get active general test."""
    stmt = select(Test).where(
        Test.test_type == TestType.GENERAL, Test.is_active == True  # noqa: E712
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_active_specialized_test(
    db: AsyncSession, specialty_code: str
) -> Test | None:
    """Get active specialized test for specialty."""
    from app.db.models.specialty import Specialty

    stmt = (
        select(Test)
        .join(Specialty, Test.specialty_id == Specialty.id)
        .where(
            Test.test_type == TestType.SPECIALIZED,
            Test.is_active == True,  # noqa: E712
            Specialty.code == specialty_code,
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
