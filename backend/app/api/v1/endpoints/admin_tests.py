"""Admin endpoints for test editor."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_admin_user_from_session, get_db
from app.crud import admin_test
from app.db.models.user import User
from app.schemas.test import (
    AnswerCreate,
    AnswerUpdate,
    QuestionCreate,
    QuestionUpdate,
    TestAdmin,
    TestCreate,
    TestUpdate,
)

router = APIRouter()


@router.get("/{test_id}", response_model=TestAdmin)
async def get_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Get test with all questions and answers for editing."""
    test = await admin_test.get_test_with_questions(db, test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found",
        )
    return test


@router.post("/", response_model=TestAdmin)
async def create_test(
    test_data: TestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Create new test."""
    test = await admin_test.create_test(db, test_data)
    await db.commit()
    return await admin_test.get_test_with_questions(db, test.id)


@router.put("/{test_id}", response_model=TestAdmin)
async def update_test(
    test_id: int,
    test_data: TestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Update test."""
    test = await admin_test.update_test(db, test_id, test_data)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found",
        )
    await db.commit()
    return await admin_test.get_test_with_questions(db, test_id)


@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Delete test."""
    success = await admin_test.delete_test(db, test_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found",
        )
    await db.commit()


@router.post("/{test_id}/questions", response_model=TestAdmin)
async def create_question(
    test_id: int,
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Create new question in test."""
    await admin_test.create_question(db, test_id, question_data)
    await db.commit()
    return await admin_test.get_test_with_questions(db, test_id)


@router.put("/questions/{question_id}", response_model=dict)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Update question."""
    question = await admin_test.update_question(db, question_id, question_data)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    await db.commit()
    return {"success": True}


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Delete question."""
    success = await admin_test.delete_question(db, question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    await db.commit()


@router.post("/questions/{question_id}/answers", response_model=dict)
async def create_answer(
    question_id: int,
    answer_data: AnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Create new answer for question."""
    await admin_test.create_answer(db, question_id, answer_data)
    await db.commit()
    return {"success": True}


@router.put("/answers/{answer_id}", response_model=dict)
async def update_answer(
    answer_id: int,
    answer_data: AnswerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Update answer."""
    answer = await admin_test.update_answer(db, answer_id, answer_data)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found",
        )
    await db.commit()
    return {"success": True}


@router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user_from_session),
):
    """Delete answer."""
    success = await admin_test.delete_answer(db, answer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found",
        )
    await db.commit()
