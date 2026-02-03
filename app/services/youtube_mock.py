"""
Mock YouTube service: generates fake channel and video data.
Used when no real YouTube API is configured.
"""
import random
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import ConnectedAccount, Video, AnalyticsSnapshot


def _random_views() -> int:
    return random.randint(100, 50000)


def _random_likes(views: int) -> int:
    return random.randint(views // 100, views // 20)


def _random_comments(views: int) -> int:
    return random.randint(views // 500, views // 100)


async def create_mock_channel(session: AsyncSession, user_id: int, channel_name: str | None = None) -> ConnectedAccount:
    """Create a mock connected YouTube channel and seed videos + snapshots."""
    name = channel_name or "My Channel"
    channel_id = f"UC_mock_{user_id}_{random.randint(1000, 9999)}"
    acc = ConnectedAccount(
        user_id=user_id,
        platform="youtube",
        channel_id=channel_id,
        channel_name=name,
    )
    session.add(acc)
    await session.flush()

    # Create mock videos
    titles = [
        "How to Get Started with Content Creation",
        "My Best Video Yet - Tips and Tricks",
        "Behind the Scenes: A Day in My Life",
        "Tutorial: Editing Like a Pro",
        "Q&A: Answering Your Questions",
        "Collaboration with Friends",
        "Weekly Vlog #1",
        "Top 10 Tips for Growth",
    ]
    for i, title in enumerate(titles[:5]):
        pub = datetime.utcnow() - timedelta(days=random.randint(7, 90))
        v = _random_views()
        vid = Video(
            connected_account_id=acc.id,
            external_id=f"vid_{acc.id}_{i}",
            title=title,
            published_at=pub,
            view_count=v,
            like_count=_random_likes(v),
            comment_count=_random_comments(v),
            duration_seconds=random.randint(180, 1200),
        )
        session.add(vid)

    # Create mock daily snapshots for last 30 days
    base_views = random.randint(5000, 20000)
    base_subs = random.randint(100, 5000)
    for d in range(30):
        snap_date = datetime.utcnow() - timedelta(days=d)
        delta = random.randint(-500, 1500)
        total_views = max(0, base_views + d * 200 + delta * 10)
        total_likes = total_views // 30
        total_comments = total_views // 100
        subs = base_subs + d * 5 + random.randint(-2, 10)
        snap = AnalyticsSnapshot(
            connected_account_id=acc.id,
            snapshot_date=snap_date,
            period_type="daily",
            total_views=total_views,
            total_likes=total_likes,
            total_comments=total_comments,
            subscriber_count=max(0, subs),
        )
        session.add(snap)

    await session.flush()
    return acc


async def get_first_connected_account(session: AsyncSession, user_id: int) -> ConnectedAccount | None:
    """Get user's first connected YouTube account."""
    result = await session.execute(
        select(ConnectedAccount).where(
            ConnectedAccount.user_id == user_id,
            ConnectedAccount.platform == "youtube",
        ).limit(1)
    )
    return result.scalars().first()
