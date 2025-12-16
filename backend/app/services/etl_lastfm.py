from sqlalchemy.orm import Session
from app.models.artist import Artist
from app.models.track import Track
from app.models.track_trend import TrackTrend
from app.services.lastfm_client import get_top_tracks_by_country
from datetime import datetime

def run_lastfm_etl(db: Session, country: str, limit: int = 50):
    items = get_top_tracks_by_country(country, limit)
    run_time = datetime.utcnow()

    for t in items:
        artist_name = t["artist"]["name"].strip()

        artist = db.query(Artist).filter(Artist.name == artist_name).first()
        if not artist:
            artist = Artist(name=artist_name)
            db.add(artist)
            db.commit()
            db.refresh(artist)

        title = t["name"].strip()
        url = t.get("url")
        mbid = t.get("mbid") or None

        track = Track(title=title, artist_id=artist.id, url=url, mbid=mbid)
        db.add(track)
        db.commit()
        db.refresh(track)

        rank = int(t["@attr"]["rank"])
        trend = TrackTrend(track_id=track.id, country=country, rank=rank, fetched_at=run_time)
        db.add(trend)
        db.commit()