"""
Weekly AI insights generator.
Creates mock suggestions for users who have connected accounts.
"""
import logging
import random
from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.tasks.celery_app import celery_app

# Use sync engine for Celery (no async in worker)
from app.core.config import settings

# Sync URL: PostgreSQL -> drop asyncpg; SQLite -> drop aiosqlite
if "asyncpg" in settings.DATABASE_URL:
    SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql")
elif "aiosqlite" in settings.DATABASE_URL:
    SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+aiosqlite", "").replace("sqlite+aiosqlite", "sqlite")
else:
    SYNC_DATABASE_URL = settings.DATABASE_URL

logger = logging.getLogger(__name__)

# Sync engine for Celery tasks
engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SUGGESTIONS = [
    ("posting_time", "Post at 6PM", "Your audience is most active around 6 PM. Try scheduling posts then."),
    ("engagement", "Your engagement is dropping", "Consider asking a question in the first 30 seconds to boost comments."),
    ("titles", "Try shorter titles", "Videos with titles under 50 characters tend to get more clicks."),
    ("thumbnail", "Update thumbnails", "A/B test thumbnails with faces vs. text to see what performs better."),
    ("consistency", "Post consistently", "Channels that post at least once a week grow 2x faster."),
    ("trending", "Use trending topics", "Check trending topics in your niche and create related content."),
]


@celery_app.task(name="app.tasks.ai_tasks.weekly_ai_insights")
def weekly_ai_insights():
    """Generate AI insights for all users. Mock: insert random suggestions."""
    from app.models.user import User
    from app.models.ai_insight import AIInsight

    db = SessionLocal()
    try:
        result = db.execute(select(User.id))
        user_ids = [r[0] for r in result.fetchall()]
        created = 0
        for uid in user_ids:
            ins_type, title, content = random.choice(SUGGESTIONS)
            insight = AIInsight(
                user_id=uid,
                insight_type=ins_type,
                title=title,
                content=content,
                priority=random.choice(["low", "medium", "high"]),
            )
            db.add(insight)
            created += 1
        db.commit()
        logger.info("Weekly AI insights: created %d for %d users", created, len(user_ids))
        return {"status": "ok", "created": created}
    except Exception as e:
        db.rollback()
        logger.exception("Weekly AI insights failed: %s", e)
        raise
    finally:
        db.close()
