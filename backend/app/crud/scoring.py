from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.answer import Answer
from app.db.models.question import Question
from app.db.models.result import TestResult
from app.db.models.specialty import Specialty
from app.schemas.test import AnswerSubmit, SpecialtyResult, TestResultResponse


async def get_max_weight_for_question(db: AsyncSession, question_id: int) -> int:
    """Get maximum weight among all answers for a question."""
    stmt = select(func.max(Answer.weight)).where(Answer.question_id == question_id)
    result = await db.execute(stmt)
    max_weight = result.scalar_one_or_none()
    return max_weight if max_weight is not None else 0


async def calculate_result(
    db: AsyncSession,
    user_id: int,
    test_id: int,
    submissions: list[AnswerSubmit],
) -> TestResultResponse:
    """
    Calculate test results based on user submissions.

    Algorithm (Multi-dimensional weights):
    1. For each submission, get the answer's weights for all specialties
    2. Add weights to each specialty's score
    3. Calculate max possible score per specialty (sum of max weights from each question)
    4. Calculate percentage for each specialty
    5. Sort by percentage descending
    6. Save result to database
    """
    from app.db.models.test import Test

    specialty_scores: dict[str, int] = defaultdict(int)
    specialty_max: dict[str, int] = defaultdict(int)
    specialty_names: dict[str, str] = {}
    processed_questions: set[int] = set()

    # Get test to check type
    test = await db.get(Test, test_id)
    if not test:
        raise ValueError(f"Test {test_id} not found")

    # Get specialties based on test type
    if test.test_type == "specialized" and test.specialty_id:
        # For specialized test, only calculate for one specialty
        specialty = await db.get(Specialty, test.specialty_id)
        if specialty:
            specialty_names[specialty.code] = specialty.name
            specialty_scores[specialty.code] = 0
            specialty_max[specialty.code] = 0
    else:
        # For general test, calculate for all specialties
        stmt = select(Specialty)
        result = await db.execute(stmt)
        all_specialties = result.scalars().all()
        for specialty in all_specialties:
            specialty_names[specialty.code] = specialty.name
            specialty_scores[specialty.code] = 0
            specialty_max[specialty.code] = 0

    for submission in submissions:
        # Get answer and question
        answer = await db.get(Answer, submission.answer_id)
        question = await db.get(Question, submission.question_id)

        if not answer or not question:
            continue

        # Add weights from this answer
        if test.test_type == "specialized" and test.specialty_id:
            # For specialized test, only count the test's specialty
            specialty = await db.get(Specialty, test.specialty_id)
            if specialty and answer.weights and specialty.code in answer.weights:
                specialty_scores[specialty.code] += answer.weights[specialty.code]
        else:
            # For general test, count all specialties
            if answer.weights:
                for specialty_code, weight in answer.weights.items():
                    if specialty_code in specialty_names:
                        specialty_scores[specialty_code] += weight
            else:
                # Fallback to legacy single weight if weights not set
                if question.specialty_id:
                    specialty = await db.get(Specialty, question.specialty_id)
                    if specialty:
                        specialty_scores[specialty.code] += answer.weight

        # Calculate max possible for this question (only once per question)
        if question.id not in processed_questions:
            processed_questions.add(question.id)

            # Get all answers for this question to find max weights per specialty
            stmt = select(Answer).where(Answer.question_id == question.id)
            result = await db.execute(stmt)
            all_answers = result.scalars().all()

            # For each specialty, find the maximum weight available in this question
            for specialty_code in specialty_names.keys():
                max_weight_for_specialty = 0
                for ans in all_answers:
                    if ans.weights and specialty_code in ans.weights:
                        max_weight_for_specialty = max(
                            max_weight_for_specialty,
                            ans.weights[specialty_code]
                        )
                specialty_max[specialty_code] += max_weight_for_specialty

    # Calculate results with percentages
    results: list[SpecialtyResult] = []
    for code in specialty_names:
        score = specialty_scores[code]
        max_score = specialty_max[code]
        percentage = round((score / max_score * 100), 1) if max_score > 0 else 0.0

        results.append(
            SpecialtyResult(
                specialty_code=code,
                specialty_name=specialty_names[code],
                score=score,
                max_score=max_score,
                percentage=percentage,
            )
        )

    # Sort by percentage descending
    results.sort(key=lambda r: r.percentage, reverse=True)

    # Save result to database
    test_result = TestResult(
        user_id=user_id,
        test_id=test_id,
        payload={"answers": [s.model_dump() for s in submissions]},
        scores={r.specialty_code: r.percentage for r in results},
    )
    db.add(test_result)
    await db.flush()
    await db.refresh(test_result)

    return TestResultResponse(
        results=results,
        recommended_specialty=results[0] if results else None,
        result_id=test_result.id,
    )


async def get_user_results(db: AsyncSession, user_id: int) -> list[TestResult]:
    """Get all test results for a user."""
    stmt = (
        select(TestResult)
        .where(TestResult.user_id == user_id)
        .order_by(TestResult.completed_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# Synchronous version for Celery workers
def calculate_result_sync(
    db: "Session",  # type: ignore
    user_id: int,
    test_id: int,
    submissions: list[AnswerSubmit],
) -> TestResult:
    """
    Synchronous version of calculate_result for Celery workers.

    Same algorithm as async version but uses sync SQLAlchemy session.
    """
    from sqlalchemy.orm import Session

    specialty_scores: dict[str, int] = defaultdict(int)
    specialty_max: dict[str, int] = defaultdict(int)
    specialty_names: dict[str, str] = {}

    for submission in submissions:
        # Get answer and question
        answer = db.get(Answer, submission.answer_id)
        question = db.get(Question, submission.question_id)

        if not answer or not question or not question.specialty_id:
            continue

        # Get specialty
        specialty = db.get(Specialty, question.specialty_id)
        if not specialty:
            continue

        code = specialty.code
        specialty_names[code] = specialty.name

        # Add answer weight to specialty score
        specialty_scores[code] += answer.weight

        # Get max weight for this question
        max_weight_result = db.execute(
            select(func.max(Answer.weight)).where(Answer.question_id == question.id)
        )
        max_weight = max_weight_result.scalar_one_or_none() or 0
        specialty_max[code] += max_weight

    # Calculate results with percentages
    results: list[SpecialtyResult] = []
    for code in specialty_scores:
        score = specialty_scores[code]
        max_score = specialty_max[code]
        percentage = round((score / max_score * 100), 1) if max_score > 0 else 0.0

        results.append(
            SpecialtyResult(
                specialty_code=code,
                specialty_name=specialty_names[code],
                score=score,
                max_score=max_score,
                percentage=percentage,
            )
        )

    # Sort by percentage descending
    results.sort(key=lambda r: r.percentage, reverse=True)

    # Save result to database
    test_result = TestResult(
        user_id=user_id,
        test_id=test_id,
        payload={"answers": [s.model_dump() for s in submissions]},
        scores={r.specialty_code: r.percentage for r in results},
    )
    db.add(test_result)
    db.commit()
    db.refresh(test_result)

    return test_result
