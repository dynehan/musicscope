import requests

BASE_URL = "https://musicbrainz.org/ws/2"
HEADERS = {
    "User-Agent": "MusicScope/1.0 ( student@example.com )"
}

def search_artist_by_name(name: str):
    params = {
        "query": f'artist:"{name}"',
        "fmt": "json",
        "limit": 1,
    }
    r = requests.get(f"{BASE_URL}/artist", params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()
    artists = data.get("artists", [])
    return artists[0] if artists else None


def get_artist_details(artist_id: str):
    params = {
        "inc": "tags",
        "fmt": "json",
    }
    r = requests.get(f"{BASE_URL}/artist/{artist_id}", params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()