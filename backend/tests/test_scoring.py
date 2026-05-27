"""Tests for scoring algorithm."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.scoring import calculate_result
from app.schemas.test import AnswerSubmit


@pytest.mark.asyncio
async def test_calculate_result_full_score(
    db_session: AsyncSession, test_user: dict, test_general_test
):
    """Test scoring with all correct answers gives 100%."""
    from app.db.models.question import Question
    from sqlalchemy import select

    # Get all questions
    stmt = select(Question).where(Question.test_id == test_general_test.id)
    result = await db_session.execute(stmt)
    questions = list(result.scalars().all())

    # Submit all best answers (weight=10)
    submissions = []
    for question in questions:
        best_answer = next(a for a in question.answers if a.weight == 10)
        submissions.append(
            AnswerSubmit(question_id=question.id, answer_id=best_answer.id)
        )

    result = await calculate_result(
        db_session, test_user["id"], test_general_test.id, submissions
    )

    assert len(result.results) > 0
    # All specialties should have 100%
    for specialty_result in result.results:
        assert specialty_result.percentage == 100.0


@pytest.mark.asyncio
async def test_calculate_result_zero_score(
    db_session: AsyncSession, test_user: dict, test_general_test
):
    """Test scoring with all wrong answers gives 0%."""
    from app.db.models.question import Question
    from sqlalchemy import select

    # Get all questions
    stmt = select(Question).where(Question.test_id == test_general_test.id)
    result = await db_session.execute(stmt)
    questions = list(result.scalars().all())

    # Submit all worst answers (weight=0)
    submissions = []
    for question in questions:
        worst_answer = next(a for a in question.answers if a.weight == 0)
        submissions.append(
            AnswerSubmit(question_id=question.id, answer_id=worst_answer.id)
        )

    result = await calculate_result(
        db_session, test_user["id"], test_general_test.id, submissions
    )

    assert len(result.results) > 0
    # All specialties should have 0%
    for specialty_result in result.results:
        assert specialty_result.percentage == 0.0


@pytest.mark.asyncio
async def test_calculate_result_mixed_score(
    db_session: AsyncSession, test_user: dict, test_general_test
):
    """Test scoring with mixed answers gives correct percentage."""
    from app.db.models.question import Question
    from sqlalchemy import select

    # Get all questions
    stmt = select(Question).where(Question.test_id == test_general_test.id)
    result = await db_session.execute(stmt)
    questions = list(result.scalars().all())

    # Submit mixed answers
    submissions = []
    for i, question in enumerate(questions):
        # Alternate between best (10) and medium (5) answers
        if i % 2 == 0:
            answer = next(a for a in question.answers if a.weight == 10)
        else:
            answer = next(a for a in question.answers if a.weight == 5)
        submissions.append(AnswerSubmit(question_id=question.id, answer_id=answer.id))

    result = await calculate_result(
        db_session, test_user["id"], test_general_test.id, submissions
    )

    assert len(result.results) > 0
    # Should have percentage between 0 and 100
    for specialty_result in result.results:
        assert 0 <= specialty_result.percentage <= 100


@pytest.mark.asyncio
async def test_recommended_specialty_is_top(
    db_session: AsyncSession, test_user: dict, test_general_test
):
    """Test that recommended specialty is the one with highest score."""
    from app.db.models.question import Question
    from sqlalchemy import select

    # Get all questions
    stmt = select(Question).where(Question.test_id == test_general_test.id)
    result = await db_session.execute(stmt)
    questions = list(result.scalars().all())

    # Submit best answers
    submissions = []
    for question in questions:
        best_answer = next(a for a in question.answers if a.weight == 10)
        submissions.append(
            AnswerSubmit(question_id=question.id, answer_id=best_answer.id)
        )

    result = await calculate_result(
        db_session, test_user["id"], test_general_test.id, submissions
    )

    assert result.recommended_specialty is not None
    # Recommended should be the first (highest percentage)
    assert result.recommended_specialty.percentage == result.results[0].percentage


@pytest.mark.asyncio
async def test_results_sorted_descending(
    db_session: AsyncSession, test_user: dict, test_general_test
):
    """Test that results are sorted by percentage descending."""
    from app.db.models.question import Question
    from sqlalchemy import select

    # Get all questions
    stmt = select(Question).where(Question.test_id == test_general_test.id)
    result = await db_session.execute(stmt)
    questions = list(result.scalars().all())

    # Submit answers
    submissions = []
    for question in questions:
        best_answer = next(a for a in question.answers if a.weight == 10)
        submissions.append(
            AnswerSubmit(question_id=question.id, answer_id=best_answer.id)
        )

    result = await calculate_result(
        db_session, test_user["id"], test_general_test.id, submissions
    )

    # Check sorting
    percentages = [r.percentage for r in result.results]
    assert percentages == sorted(percentages, reverse=True)


@pytest.mark.asyncio
async def test_result_saved_to_database(
    db_session: AsyncSession, test_user: dict, test_general_test
):
    """Test that result is saved to database."""
    from app.db.models.question import Question
    from app.db.models.result import TestResult
    from sqlalchemy import select

    # Get all questions
    stmt = select(Question).where(Question.test_id == test_general_test.id)
    result = await db_session.execute(stmt)
    questions = list(result.scalars().all())

    # Submit answers
    submissions = []
    for question in questions:
        best_answer = next(a for a in question.answers if a.weight == 10)
        submissions.append(
            AnswerSubmit(question_id=question.id, answer_id=best_answer.id)
        )

    result = await calculate_result(
        db_session, test_user["id"], test_general_test.id, submissions
    )

    # Check database
    saved_result = await db_session.get(TestResult, result.result_id)
    assert saved_result is not None
    assert saved_result.user_id == test_user["id"]
    assert saved_result.test_id == test_general_test.id
    assert len(saved_result.scores) > 0
