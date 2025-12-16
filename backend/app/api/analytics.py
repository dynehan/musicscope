from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db
from app.models.track_trend import TrackTrend
from app.models.track import Track
from app.models.artist import Artist

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/genre-distribution")
def genre_distribution(
    country: str,
    top_n: int = 10,
    db: Session = Depends(get_db),
):
    """
    Returns genre distribution for the latest fetched_at snapshot in a given country.
    genres are stored as CSV in artists.genres (e.g., "pop,rock,indie").
    """

    # 1) find latest snapshot time for that country
    latest_time = (
        db.query(func.max(TrackTrend.fetched_at))
        .filter(TrackTrend.country == country)
        .scalar()
    )

    if not latest_time:
        return {
            "country": country,
            "latest_fetched_at": None,
            "total_tracks": 0,
            "top_n": top_n,
            "genres": [],
            "note": "No track_trends data for this country yet. Run Last.fm ETL first.",
        }

    # 2) get artists.genres for tracks in the latest snapshot
    rows = (
        db.query(Artist.genres)
        .join(Track, Track.artist_id == Artist.id)
        .join(TrackTrend, TrackTrend.track_id == Track.id)
        .filter(TrackTrend.country == country, TrackTrend.fetched_at == latest_time)
        .all()
    )

    total_tracks = len(rows)
    counter = Counter()

    for (genres_csv,) in rows:
        if not genres_csv:
            continue
        parts = [g.strip().lower() for g in genres_csv.split(",") if g.strip()]
        counter.update(parts)

    total_tags = sum(counter.values())

    # If no genres exist yet (MusicBrainz ETL not run or no tags found)
    if total_tags == 0:
        return {
            "country": country,
            "latest_fetched_at": latest_time,
            "total_tracks": total_tracks,
            "top_n": top_n,
            "genres": [],
            "note": "No genre tags found. Run MusicBrainz ETL to enrich artists.genres.",
        }

    top = counter.most_common(top_n)

    result = [
        {
            "genre": genre,
            "count": count,
            "percentage": round((count / total_tags) * 100, 2),
        }
        for genre, count in top
    ]

    return {
        "country": country,
        "latest_fetched_at": latest_time,
        "total_tracks": total_tracks,
        "top_n": top_n,
        "total_genre_tags_counted": total_tags,
        "genres": result,
    }


@router.get("/top-artists-by-country")
def top_artists_by_country(
    country: str,
    top_n: int = 10,
    db: Session = Depends(get_db),
):
    """Return top artists for the latest snapshot in a given country.

    We count how many tracks each artist has in the latest `track_trends` snapshot for `country`.
    """

    latest_time = (
        db.query(func.max(TrackTrend.fetched_at))
        .filter(TrackTrend.country == country)
        .scalar()
    )

    if not latest_time:
        return {
            "country": country,
            "latest_fetched_at": None,
            "top_n": top_n,
            "artists": [],
            "note": "No track_trends data for this country yet. Run Last.fm ETL first.",
        }

    rows = (
        db.query(
            Artist.id.label("artist_id"),
            Artist.name.label("artist_name"),
            Artist.country.label("artist_country"),
            Artist.genres.label("genres"),
            func.count(Track.id).label("track_count"),
        )
        .join(Track, Track.artist_id == Artist.id)
        .join(TrackTrend, TrackTrend.track_id == Track.id)
        .filter(
            TrackTrend.country == country,
            TrackTrend.fetched_at == latest_time,
        )
        .group_by(Artist.id)
        .order_by(func.count(Track.id).desc())
        .limit(top_n)
        .all()
    )

    artists = []
    for r in rows:
        genres_list = [g.strip() for g in (r.genres or "").split(",") if g.strip()]
        artists.append(
            {
                "artist_id": r.artist_id,
                "artist_name": r.artist_name,
                "artist_country": r.artist_country,
                "genres": genres_list[:5],
                "track_count": r.track_count,
            }
        )

    return {
        "country": country,
        "latest_fetched_at": latest_time,
        "top_n": top_n,
        "artists": artists,
    }
    
@router.get("/artist-nationality-distribution")
def artist_nationality_distribution(
    country: str,
    top_n: int = 10,
    db: Session = Depends(get_db),
):
    """
    Returns distribution of artist nationalities
    for the latest snapshot in a given country.
    """

    # 1) latest snapshot time
    latest_time = (
        db.query(func.max(TrackTrend.fetched_at))
        .filter(TrackTrend.country == country)
        .scalar()
    )

    if not latest_time:
        return {
            "country": country,
            "latest_fetched_at": None,
            "top_n": top_n,
            "nationalities": [],
            "note": "No track_trends data. Run Last.fm ETL first.",
        }

    # 2) count artist countries
    rows = (
        db.query(
            Artist.country.label("artist_country"),
            func.count(func.distinct(Artist.id)).label("artist_count"),
        )
        .join(Track, Track.artist_id == Artist.id)
        .join(TrackTrend, TrackTrend.track_id == Track.id)
        .filter(
            TrackTrend.country == country,
            TrackTrend.fetched_at == latest_time,
            Artist.country.isnot(None),
        )
        .group_by(Artist.country)
        .order_by(func.count(func.distinct(Artist.id)).desc())
        .limit(top_n)
        .all()
    )

    total_artists = sum(r.artist_count for r in rows)

    result = [
        {
            "artist_country": r.artist_country,
            "count": r.artist_count,
            "percentage": round((r.artist_count / total_artists) * 100, 2)
            if total_artists > 0 else 0,
        }
        for r in rows
    ]

    return {
        "country": country,
        "latest_fetched_at": latest_time,
        "total_artists": total_artists,
        "top_n": top_n,
        "nationalities": result,
    }
    
@router.get("/country-genre-comparison")
def country_genre_comparison(
    c1: str,
    c2: str,
    top_n: int = 10,
    db: Session = Depends(get_db),
):
    """
    Compare genre distributions between two countries using the latest snapshot for each.
    Genres come from artists.genres (CSV string).
    """

    def _latest_time(country: str):
        return (
            db.query(func.max(TrackTrend.fetched_at))
            .filter(TrackTrend.country == country)
            .scalar()
        )

    def _genre_counter(country: str, latest_time):
        rows = (
            db.query(Artist.genres)
            .join(Track, Track.artist_id == Artist.id)
            .join(TrackTrend, TrackTrend.track_id == Track.id)
            .filter(TrackTrend.country == country, TrackTrend.fetched_at == latest_time)
            .all()
        )
        counter = Counter()
        for (genres_csv,) in rows:
            if not genres_csv:
                continue
            parts = [g.strip().lower() for g in genres_csv.split(",") if g.strip()]
            counter.update(parts)
        return counter, len(rows)

    latest_1 = _latest_time(c1)
    latest_2 = _latest_time(c2)

    if not latest_1 or not latest_2:
        return {
            "country_1": c1,
            "country_2": c2,
            "latest_fetched_at_1": latest_1,
            "latest_fetched_at_2": latest_2,
            "top_n": top_n,
            "genres": [],
            "note": "Missing snapshot data for one or both countries. Run Last.fm ETL for both countries first.",
        }

    counter_1, total_tracks_1 = _genre_counter(c1, latest_1)
    counter_2, total_tracks_2 = _genre_counter(c2, latest_2)

    total_tags_1 = sum(counter_1.values())
    total_tags_2 = sum(counter_2.values())

    if total_tags_1 == 0 or total_tags_2 == 0:
        return {
            "country_1": c1,
            "country_2": c2,
            "latest_fetched_at_1": latest_1,
            "latest_fetched_at_2": latest_2,
            "total_tracks_1": total_tracks_1,
            "total_tracks_2": total_tracks_2,
            "total_genre_tags_1": total_tags_1,
            "total_genre_tags_2": total_tags_2,
            "top_n": top_n,
            "genres": [],
            "note": "One or both countries have no genre tags. Run MusicBrainz ETL to enrich artists.genres.",
        }

    # pick top genres based on combined popularity across both countries
    combined = counter_1 + counter_2
    top_genres = [g for g, _ in combined.most_common(top_n)]

    comparison = []
    for genre in top_genres:
        c1_count = counter_1.get(genre, 0)
        c2_count = counter_2.get(genre, 0)
        comparison.append({
            "genre": genre,
            "c1_count": c1_count,
            "c1_percentage": round((c1_count / total_tags_1) * 100, 2),
            "c2_count": c2_count,
            "c2_percentage": round((c2_count / total_tags_2) * 100, 2),
        })

    return {
        "country_1": c1,
        "country_2": c2,
        "latest_fetched_at_1": latest_1,
        "latest_fetched_at_2": latest_2,
        "total_tracks_1": total_tracks_1,
        "total_tracks_2": total_tracks_2,
        "total_genre_tags_1": total_tags_1,
        "total_genre_tags_2": total_tags_2,
        "top_n": top_n,
        "genres": comparison,
    }