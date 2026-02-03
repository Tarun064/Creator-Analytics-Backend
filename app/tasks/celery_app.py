"""Celery app configuration."""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "creator_analytics",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.sync_tasks", "app.tasks.ai_tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
