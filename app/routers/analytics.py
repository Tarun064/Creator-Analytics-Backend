"""Analytics routes: overview, videos, growth."""
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models import ConnectedAccount, Video, AnalyticsSnapshot
from app.schemas.analytics import (
    OverviewResponse,
    VideoAnalyticsItem,
    VideosListResponse,
    GrowthPoint,
    GrowthResponse,
)
from app.auth.jwt import get_current_user_id
from app.services.youtube_mock import get_first_connected_account
from app.utils.redis_client import cache_get, cache_set

logger = logging.getLogger(__name__)
router = APIRouter()

# Cache TTL for analytics (5 min)
CACHE_TTL = 300


@router.get("/overview", response_model=OverviewResponse)
async def analytics_overview(
    period_days: int = Query(30, ge=1, le=90),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics overview for dashboard. Cached by Redis."""
    cache_key = f"analytics:overview:{user_id}:{period_days}"
    cached = await cache_get(cache_key)
    if cached:
        return OverviewResponse(**cached)

    acc = await get_first_connected_account(db, user_id)
    if not acc:
        return OverviewResponse(
            total_views=0, total_likes=0, total_comments=0, total_videos=0,
            subscriber_count=0, period_days=period_days,
        )

    since = datetime.utcnow() - timedelta(days=period_days)
    # Sum video stats for period
    vid_result = await db.execute(
        select(
            func.coalesce(func.sum(Video.view_count), 0).label("views"),
            func.coalesce(func.sum(Video.like_count), 0).label("likes"),
            func.coalesce(func.sum(Video.comment_count), 0).label("comments"),
            func.count(Video.id).label("count"),
        ).where(Video.connected_account_id == acc.id)
    )
    row = vid_result.one()
    # Latest subscriber count from snapshot
    sub_result = await db.execute(
        select(AnalyticsSnapshot.subscriber_count)
        .where(
            AnalyticsSnapshot.connected_account_id == acc.id,
            AnalyticsSnapshot.snapshot_date <= datetime.utcnow(),
        )
        .order_by(AnalyticsSnapshot.snapshot_date.desc())
        .limit(1)
    )
    sub_row = sub_result.scalars().first()
    subscriber_count = int(sub_row) if sub_row is not None else 0

    resp = OverviewResponse(
        total_views=int(row.views),
        total_likes=int(row.likes),
        total_comments=int(row.comments),
        total_videos=int(row.count),
        subscriber_count=subscriber_count,
        period_days=period_days,
    )
    await cache_set(cache_key, resp.model_dump(), ttl_seconds=CACHE_TTL)
    return resp


@router.get("/videos", response_model=VideosListResponse)
async def analytics_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of videos with analytics."""
    acc = await get_first_connected_account(db, user_id)
    if not acc:
        return VideosListResponse(items=[], total=0, page=page, page_size=page_size)

    count_result = await db.execute(
        select(func.count(Video.id)).where(Video.connected_account_id == acc.id)
    )
    total = count_result.scalar() or 0
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Video)
        .where(Video.connected_account_id == acc.id)
        .order_by(Video.published_at.desc().nullslast())
        .offset(offset)
        .limit(page_size)
    )
    videos = result.scalars().all()
    items = [VideoAnalyticsItem.model_validate(v) for v in videos]
    return VideosListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/growth", response_model=GrowthResponse)
async def analytics_growth(
    period_days: int = Query(30, ge=1, le=90),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get growth chart data (daily snapshots). Cached."""
    cache_key = f"analytics:growth:{user_id}:{period_days}"
    cached = await cache_get(cache_key)
    if cached:
        return GrowthResponse(**cached)

    acc = await get_first_connected_account(db, user_id)
    if not acc:
        return GrowthResponse(data=[], period_days=period_days)

    since = datetime.utcnow() - timedelta(days=period_days)
    result = await db.execute(
        select(AnalyticsSnapshot)
        .where(
            AnalyticsSnapshot.connected_account_id == acc.id,
            AnalyticsSnapshot.snapshot_date >= since,
            AnalyticsSnapshot.period_type == "daily",
        )
        .order_by(AnalyticsSnapshot.snapshot_date.asc())
    )
    snapshots = result.scalars().all()
    data = [
        GrowthPoint(
            date=s.snapshot_date.strftime("%Y-%m-%d"),
            views=int(s.total_views),
            likes=int(s.total_likes),
            comments=int(s.total_comments),
            subscribers=int(s.subscriber_count),
        )
        for s in snapshots
    ]
    resp = GrowthResponse(data=data, period_days=period_days)
    await cache_set(cache_key, resp.model_dump(), ttl_seconds=CACHE_TTL)
    return resp
