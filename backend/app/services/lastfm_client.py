import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://ws.audioscrobbler.com/2.0/"

def get_top_tracks_by_country(country: str, limit: int = 20):
    api_key = os.getenv("LASTFM_API_KEY")  
    if not api_key:
        raise RuntimeError("LASTFM_API_KEY is not set")

    params = {
        "method": "geo.getTopTracks",
        "country": country,
        "api_key": api_key,
        "format": "json",
        "limit": limit,
    }

    r = requests.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    if "error" in data:
        raise RuntimeError(f"Last.fm API error {data.get('error')}: {data.get('message')}")

    return data["tracks"]["track"]