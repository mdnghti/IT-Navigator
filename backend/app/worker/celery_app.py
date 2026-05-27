"""Celery application configuration."""

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
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_expires = 3600
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.worker"])
