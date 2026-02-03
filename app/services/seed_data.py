"""
Seed dummy data on first run so the app shows data without "Connect YouTube".
Creates demo user + channel + videos + analytics snapshots + AI insights.
"""
import logging
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models import User, AIInsight
from app.auth.password import hash_password
from app.services.youtube_mock import create_mock_channel

logger = logging.getLogger(__name__)

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo123"
DEMO_NAME = "Demo User"

AI_INSIGHTS_DATA = [
    ("posting_time", "Post at 6PM", "Your audience is most active around 6 PM. Try scheduling posts then.", "high"),
    ("engagement", "Your engagement is dropping", "Consider asking a question in the first 30 seconds to boost comments.", "medium"),
    ("titles", "Try shorter titles", "Videos with titles under 50 characters tend to get more clicks.", "medium"),
    ("thumbnail", "Update thumbnails", "A/B test thumbnails with faces vs. text to see what performs better.", "low"),
    ("consistency", "Post consistently", "Channels that post at least once a week grow 2x faster.", "high"),
    ("trending", "Use trending topics", "Check trending topics in your niche and create related content.", "medium"),
]


async def seed_if_empty():
    """Ensure demo user exists; if no users existed, also create channel + videos + insights."""
    async with async_session_maker() as session:
        # Check if demo user already exists
        demo_result = await session.execute(select(User).where(User.email == DEMO_EMAIL))
        demo_user = demo_result.scalars().first()

        # Check if we have any users (for full seed)
        any_user_result = await session.execute(select(User).limit(1))
        had_users = any_user_result.scalars().first() is not None

        if demo_user is None:
            logger.info("Creating demo user %s (login: %s / %s)", DEMO_EMAIL, DEMO_EMAIL, DEMO_PASSWORD)
            demo_user = User(
                email=DEMO_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
                full_name=DEMO_NAME,
            )
            session.add(demo_user)
            await session.flush()

        if had_users:
            # Only needed to add demo user
            await session.commit()
            logger.info("Demo user ready. Login with %s / %s", DEMO_EMAIL, DEMO_PASSWORD)
            return

        # No users existed: full seed (demo + channel + videos + insights)
        logger.info("Seeding full dummy data (channel + videos + insights)...")
        await create_mock_channel(session, demo_user.id, "Demo Creator Channel")
        await session.flush()

        for ins_type, title, content, priority in AI_INSIGHTS_DATA:
            insight = AIInsight(
                user_id=demo_user.id,
                insight_type=ins_type,
                title=title,
                content=content,
                priority=priority,
            )
            session.add(insight)

        await session.commit()
        logger.info("Seed complete. Login with %s / %s", DEMO_EMAIL, DEMO_PASSWORD)
