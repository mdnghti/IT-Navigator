import random
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.crud import scoring, test as test_crud
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.test import (
    QuestionRead,
    TestResultRead,
    TestResultResponse,
    TestSubmitRequest,
)

router = APIRouter()


@router.get("/general/questions", response_model=list[QuestionRead])
async def get_general_questions(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[QuestionRead]:
    """Get all questions for general test with shuffled order."""
    questions = await test_crud.get_general_test_questions(db)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active general test found",
        )

    # Shuffle questions
    random.shuffle(questions)

    # Convert to Pydantic models and shuffle answers
    result = []
    for question in questions:
        # Get all answers as a list
        answers_list = list(question.answers)
        # Shuffle the list
        random.shuffle(answers_list)
        # Create QuestionRead with shuffled answers
        q_dict = {
            "id": question.id,
            "text": question.text,
            "answers": answers_list,
        }
        result.append(QuestionRead.model_validate(q_dict))

    return result


@router.post("/general/submit", response_model=TestResultResponse)
async def submit_general_test(
    body: TestSubmitRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TestResultResponse:
    """Submit general test answers and get results."""
    general_test = await test_crud.get_active_general_test(db)

    if not general_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active general test found",
        )

    if not body.answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No answers provided",
        )

    result = await scoring.calculate_result(
        db, current_user.id, general_test.id, body.answers
    )

    await db.commit()

    return result


@router.get("/specialized/{specialty_code}/questions", response_model=list[QuestionRead])
async def get_specialized_questions(
    specialty_code: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[QuestionRead]:
    """Get all questions for specialized test by specialty code."""
    questions = await test_crud.get_specialized_test_questions(db, specialty_code)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active specialized test found for specialty {specialty_code}",
        )

    # Shuffle questions
    random.shuffle(questions)

    # Convert to Pydantic models and shuffle answers
    result = []
    for question in questions:
        # Get all answers as a list
        answers_list = list(question.answers)
        # Shuffle the list
        random.shuffle(answers_list)
        # Create QuestionRead with shuffled answers
        q_dict = {
            "id": question.id,
            "text": question.text,
            "answers": answers_list,
        }
        result.append(QuestionRead.model_validate(q_dict))

    return result


@router.post("/specialized/{specialty_code}/submit", response_model=TestResultResponse)
async def submit_specialized_test(
    specialty_code: str,
    body: TestSubmitRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TestResultResponse:
    """Submit specialized test answers and get results."""
    test = await test_crud.get_active_specialized_test(db, specialty_code)

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active specialized test found for specialty {specialty_code}",
        )

    if not body.answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No answers provided",
        )

    result = await scoring.calculate_result(db, current_user.id, test.id, body.answers)

    await db.commit()

    return result


@router.get("/results/my", response_model=list[TestResultRead])
async def get_my_results(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TestResultRead]:
    """Get all test results for current user."""
    from sqlalchemy import select
    from app.db.models.specialty import Specialty

    # Fetch all specialties to map codes to names
    spec_stmt = select(Specialty)
    spec_res = await db.execute(spec_stmt)
    specialties = spec_res.scalars().all()
    spec_names = {s.code: s.name for s in specialties}

    results = await scoring.get_user_results(db, current_user.id)

    return [
        TestResultRead(
            id=r.id,
            test_id=r.test_id,
            scores=r.scores,
            completed_at=r.completed_at.isoformat(),
            specialty_names=spec_names,
        )
        for r in results
    ]


@router.get("/results/{result_id}", response_model=TestResultRead)
async def get_result_by_id(
    result_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TestResultRead:
    """Get specific test result by ID."""
    from sqlalchemy import select
    from app.db.models.result import TestResult
    from app.db.models.specialty import Specialty

    result = await db.get(TestResult, result_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found",
        )

    if result.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this result",
        )

    # Fetch all specialties to map codes to names
    spec_stmt = select(Specialty)
    spec_res = await db.execute(spec_stmt)
    specialties = spec_res.scalars().all()
    spec_names = {s.code: s.name for s in specialties}

    return TestResultRead(
        id=result.id,
        test_id=result.test_id,
        scores=result.scores,
        completed_at=result.completed_at.isoformat(),
        specialty_names=spec_names,
    )

