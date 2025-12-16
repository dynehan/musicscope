from sqlalchemy.orm import Session
from app.models.artist import Artist
from app.services.musicbrainz_client import (
    search_artist_by_name,
    get_artist_details,
)
import time  # 🔥 추가

def run_musicbrainz_etl(db: Session, limit: int = 20):
    artists = (
        db.query(Artist)
        .filter(Artist.country.is_(None))
        .limit(limit)
        .all()
    )

    updated = 0

    for artist in artists:
        # 🔥 search 요청
        result = search_artist_by_name(artist.name)
        time.sleep(1)  # 🔥 rate limit 대응

        if not result:
            continue

        mbid = result.get("id")

        # 🔥 detail 요청
        details = get_artist_details(mbid)
        time.sleep(1)  # 🔥 rate limit 대응

        artist.musicbrainz_id = mbid
        artist.country = details.get("country")

        tags = details.get("tags", [])
        genres = [t["name"] for t in tags[:5]]

        artist.genres = ",".join(genres) if genres else None

        db.add(artist)
        updated += 1

    db.commit()
    return updated