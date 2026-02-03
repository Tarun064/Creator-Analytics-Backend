"""Video model (from YouTube)."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, BigInteger, Column
from sqlalchemy.orm import relationship

from app.core.database import Base


class Video(Base):
    """Video from connected channel."""

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    connected_account_id = Column(Integer, ForeignKey("connected_accounts.id"), nullable=False)
    external_id = Column(String(255), nullable=False, index=True)  # YouTube video ID
    title = Column(String(512), nullable=True)
    published_at = Column(DateTime, nullable=True)
    view_count = Column(BigInteger, default=0)
    like_count = Column(BigInteger, default=0)
    comment_count = Column(BigInteger, default=0)
    duration_seconds = Column(Integer, nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    connected_account = relationship("ConnectedAccount", back_populates="videos")
