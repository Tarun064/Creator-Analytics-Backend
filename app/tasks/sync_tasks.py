"""
Daily sync task: mock YouTube data sync.
In production this would call YouTube Data API.
"""
import logging
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.sync_tasks.daily_sync")
def daily_sync():
    """Daily job: sync YouTube data for all connected accounts. Mock: no-op for now."""
    logger.info("Daily sync task ran (mock - no real API)")
    return {"status": "ok", "message": "Mock daily sync completed"}
