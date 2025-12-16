from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.core.database import Base

class TrackTrend(Base):
    __tablename__ = "track_trends"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"))
    country = Column(String, index=True)  # last.fm country
    rank = Column(Integer)                # chart position
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)