"""YouTube / connected account schemas."""
from datetime import datetime
from pydantic import BaseModel


class YouTubeConnectRequest(BaseModel):
    """Request to connect YouTube (mock: we just create a fake channel)."""
    channel_name: str | None = "My Channel"


class ConnectedAccountResponse(BaseModel):
    """Connected account in API responses."""
    id: int
    platform: str
    channel_id: str | None
    channel_name: str | None
    created_at: datetime

    class Config:
        from_attributes = True
