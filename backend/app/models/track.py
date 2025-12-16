from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    lastfm_id = Column(String, index=True, nullable=True)
    mbid = Column(String, index=True, nullable=True)  # last.fm이 주는 mbid
    title = Column(String, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"))
    duration = Column(Integer, nullable=True)  # 초 단위
    url = Column(String, nullable=True)

    artist = relationship("Artist", backref="tracks")