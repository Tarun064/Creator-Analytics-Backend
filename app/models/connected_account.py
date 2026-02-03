"""Connected account (e.g. YouTube channel)."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Column
from sqlalchemy.orm import relationship

from app.core.database import Base


class ConnectedAccount(Base):
    """Linked YouTube (or other) account."""

    __tablename__ = "connected_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(50), nullable=False, default="youtube")
    channel_id = Column(String(255), nullable=True)
    channel_name = Column(String(255), nullable=True)
    access_token = Column(String(512), nullable=True)
    refresh_token = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="connected_accounts")
    videos = relationship("Video", back_populates="connected_account", cascade="all, delete-orphan")
    snapshots = relationship("AnalyticsSnapshot", back_populates="connected_account", cascade="all, delete-orphan")
