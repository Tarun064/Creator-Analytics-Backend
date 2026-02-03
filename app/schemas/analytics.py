"""Analytics API schemas."""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class OverviewResponse(BaseModel):
    """Analytics overview for dashboard."""
    total_views: int
    total_likes: int
    total_comments: int
    total_videos: int
    subscriber_count: int
    period_days: int


class VideoAnalyticsItem(BaseModel):
    """Single video in analytics list."""
    id: int
    external_id: str
    title: str | None
    view_count: int
    like_count: int
    comment_count: int
    published_at: datetime | None
    thumbnail_url: str | None

    class Config:
        from_attributes = True


class VideosListResponse(BaseModel):
    """Paginated list of videos."""
    items: list[VideoAnalyticsItem]
    total: int
    page: int
    page_size: int


class GrowthPoint(BaseModel):
    """Single point in growth chart."""
    date: str
    views: int
    likes: int
    comments: int
    subscribers: int


class GrowthResponse(BaseModel):
    """Growth chart data."""
    data: list[GrowthPoint]
    period_days: int
