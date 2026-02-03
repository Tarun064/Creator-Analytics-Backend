"""AI suggestions routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.ai_insight import AIInsight
from app.schemas.ai import AISuggestionItem, SuggestionsResponse
from app.auth.jwt import get_current_user_id

router = APIRouter()


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    limit: int = Query(20, ge=1, le=50),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated suggestions for the user."""
    result = await db.execute(
        select(AIInsight)
        .where(AIInsight.user_id == user_id)
        .order_by(AIInsight.created_at.desc())
        .limit(limit)
    )
    insights = result.scalars().all()
    cnt = await db.execute(select(func.count(AIInsight.id)).where(AIInsight.user_id == user_id))
    total = cnt.scalar() or 0
    items = [AISuggestionItem.model_validate(i) for i in insights]
    return SuggestionsResponse(items=items, total=total)
