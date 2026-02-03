"""YouTube routes: connect channel (mock)."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.youtube import YouTubeConnectRequest, ConnectedAccountResponse
from app.auth.jwt import get_current_user_id
from app.services.youtube_mock import create_mock_channel

router = APIRouter()


@router.post("/connect", response_model=ConnectedAccountResponse)
async def connect_youtube(
    body: YouTubeConnectRequest | None = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Connect YouTube channel. Mock: creates fake channel and data."""
    channel_name = body.channel_name if body else "My Channel"
    acc = await create_mock_channel(db, user_id, channel_name)
    await db.flush()
    await db.refresh(acc)
    return ConnectedAccountResponse.model_validate(acc)
