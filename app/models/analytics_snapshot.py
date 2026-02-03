"""Analytics snapshot (daily/weekly aggregates)."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, BigInteger, Column
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalyticsSnapshot(Base):
    """Daily or weekly snapshot of channel analytics."""

    __tablename__ = "analytics_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    connected_account_id = Column(Integer, ForeignKey("connected_accounts.id"), nullable=False)
    snapshot_date = Column(DateTime, nullable=False)  # date of snapshot
    period_type = Column(String(20), nullable=False)  # "daily" or "weekly"
    total_views = Column(BigInteger, default=0)
    total_likes = Column(BigInteger, default=0)
    total_comments = Column(BigInteger, default=0)
    subscriber_count = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    connected_account = relationship("ConnectedAccount", back_populates="snapshots")
