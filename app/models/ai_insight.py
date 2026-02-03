"""AI-generated insight for the user."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, Column, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class AIInsight(Base):
    """AI suggestion or insight for the creator."""

    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    insight_type = Column(String(50), nullable=False)  # e.g. "posting_time", "engagement"
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ai_insights")
