from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import datetime

class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    musicbrainz_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, index=True)
    country = Column(String, nullable=True)
    genres = Column(String, nullable=True)  # 일단 csv 문자열로 저장해도 됨
    created_at = Column(DateTime, default=datetime.utcnow)