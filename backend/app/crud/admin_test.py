"""CRUD operations for admin test editor."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.answer import Answer
from app.db.models.question import Question
from app.db.models.test import Test
from app.schemas.test import (
    AnswerCreate,
    AnswerUpdate,
    QuestionCreate,
    QuestionUpdate,
    TestCreate,
    TestUpdate,
)


async def get_test_with_questions(db: AsyncSession, test_id: int) -> Test | None:
    """Get test with all questions and answers."""
    stmt = (
        select(Test)
        .where(Test.id == test_id)
        .options(
            selectinload(Test.questions).selectinload(Question.answers),
            selectinload(Test.questions).selectinload(Question.specialty),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_test(db: AsyncSession, test_data: TestCreate) -> Test:
    """Create new test."""
    test = Test(**test_data.model_dump())
    db.add(test)
    await db.flush()
    await db.refresh(test)
    return test


async def update_test(db: AsyncSession, test_id: int, test_data: TestUpdate) -> Test | None:
    """Update test."""
    test = await db.get(Test, test_id)
    if not test:
        return None

    update_data = test_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test, field, value)

    await db.flush()
    await db.refresh(test)
    return test


async def delete_test(db: AsyncSession, test_id: int) -> bool:
    """Delete test."""
    test = await db.get(Test, test_id)
    if not test:
        return False

    await db.delete(test)
    await db.flush()
    return True


async def create_question(
    db: AsyncSession, test_id: int, question_data: QuestionCreate
) -> Question:
    """Create new question with answers."""
    question = Question(
        test_id=test_id,
        text=question_data.text,
        specialty_id=question_data.specialty_id,
        order=question_data.order,
    )
    db.add(question)
    await db.flush()

    # Create answers
    for answer_data in question_data.answers:
        answer = Answer(
            question_id=question.id,
            text=answer_data.text,
            weights=answer_data.weights,
            weight=answer_data.weight,
        )
        db.add(answer)

    await db.flush()
    await db.refresh(question)
    return question


async def update_question(
    db: AsyncSession, question_id: int, question_data: QuestionUpdate
) -> Question | None:
    """Update question."""
    question = await db.get(Question, question_id)
    if not question:
        return None

    update_data = question_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)

    await db.flush()
    await db.refresh(question)
    return question


async def delete_question(db: AsyncSession, question_id: int) -> bool:
    """Delete question and its answers."""
    question = await db.get(Question, question_id)
    if not question:
        return False

    await db.delete(question)
    await db.flush()
    return True


async def create_answer(
    db: AsyncSession, question_id: int, answer_data: AnswerCreate
) -> Answer:
    """Create new answer."""
    answer = Answer(
        question_id=question_id,
        text=answer_data.text,
        weights=answer_data.weights,
        weight=answer_data.weight,
    )
    db.add(answer)
    await db.flush()
    await db.refresh(answer)
    return answer


async def update_answer(
    db: AsyncSession, answer_id: int, answer_data: AnswerUpdate
) -> Answer | None:
    """Update answer."""
    answer = await db.get(Answer, answer_id)
    if not answer:
        return None

    update_data = answer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(answer, field, value)

    await db.flush()
    await db.refresh(answer)
    return answer


async def delete_answer(db: AsyncSession, answer_id: int) -> bool:
    """Delete answer."""
    answer = await db.get(Answer, answer_id)
    if not answer:
        return False

    await db.delete(answer)
    await db.flush()
    return True
