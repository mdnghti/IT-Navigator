"""Celery tasks for background processing."""

import logging
from typing import Any

from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, name="app.worker.tasks.run_scoring")
def run_scoring(
    self: Any, user_id: int, test_id: int, answers: list[dict[str, int]]
) -> dict[str, Any]:
    """
    Calculate test results in background.

    Synchronous scoring in worker, result is written to DB.
    """
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session

        from app.core.config import settings
        from app.crud.scoring import calculate_result_sync
        from app.schemas.test import AnswerSubmit

        # Create sync engine for Celery worker
        engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))

        with Session(engine) as db:
            answer_submissions = [AnswerSubmit(**a) for a in answers]
            result = calculate_result_sync(db, user_id, test_id, answer_submissions)

            logger.info(
                "Scoring completed for user %s, test %s, result_id %s",
                user_id,
                test_id,
                result.id,
            )

            return {
                "result_id": result.id,
                "scores": result.scores,
                "status": "completed",
            }

    except Exception as exc:
        logger.error("Scoring failed for user %s: %s", user_id, exc)
        raise self.retry(exc=exc, countdown=5)
