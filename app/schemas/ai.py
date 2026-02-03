"""AI suggestions schemas."""
from datetime import datetime
from pydantic import BaseModel


class AISuggestionItem(BaseModel):
    """Single AI suggestion."""
    id: int
    insight_type: str
    title: str
    content: str
    priority: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestionsResponse(BaseModel):
    """List of AI suggestions."""
    items: list[AISuggestionItem]
    total: int
