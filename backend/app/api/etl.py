from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.services.etl_lastfm import run_lastfm_etl
from app.services.etl_musicbrainz import run_musicbrainz_etl
from fastapi import HTTPException

router = APIRouter(prefix="/etl", tags=["ETL"])

@router.post("/lastfm/run")
def run_lastfm(country: str = "spain", limit: int = 20, db: Session = Depends(get_db)):
    try:
        run_lastfm_etl(db, country, limit)
        return {"status": "ok", "country": country, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/musicbrainz/run")
def run_musicbrainz(limit: int = 20, db: Session = Depends(get_db)):
    try:
        updated = run_musicbrainz_etl(db, limit)
        return {"status": "ok", "updated_artists": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))