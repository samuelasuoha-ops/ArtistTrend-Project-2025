import os
import requests

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_spotify_token():
    # Retrieves a Spotify access token using Client Credentials Flow.
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise ValueError("Spotify Client ID or Secret is not set. Check your .env file.")

    token_url = "https://accounts.spotify.com/api/token"


    auth = (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    data = {"grant_type": "client_credentials"}

    response = requests.post(token_url, data=data, auth=auth)
    response.raise_for_status()

    return response.json()["access_token"]


def search_artist(name):
    # Searches Spotify for an artist by name.
    token = get_spotify_token()

    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": name, "type": "artist", "limit": 5}

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    artists = []
    items = data.get("artists", {}).get("items", [])

    for item in items:
        artists.append({
            "spotify_id": item["id"],
            "name": item["name"],
            "genres": ", ".join(item.get("genres", [])),
            "followers": item.get("followers", {}).get("total", 0),
            "popularity": item.get("popularity", 0),
            "image": item["images"][0]["url"] if item.get("images") else None
        })

    return artists

def get_artist_top_tracks(spotify_id, market="US"):
    #Returns a list of the artist's top tracks from Spotify.
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{spotify_id}/top-tracks"
    params = {"market": market}

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()

    tracks = []
    for t in data.get("tracks", []):
        tracks.append({
            "name": t["name"],
            "album": t["album"]["name"],
            "preview_url": t.get("preview_url"),
            "spotify_url": t["external_urls"]["spotify"],
        })
    return tracks

def get_artist_metrics(spotify_id):
    
    # Gets current followers, genres and popularity for a single artist by Spotify ID. Returns a dict or raises for HTTP errors.
    
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{spotify_id}"

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    return {
        "followers": data.get("followers", {}).get("total", 0),
        "genres": ", ".join(data.get("genres", [])),
        "popularity": data.get("popularity", 0),
    }
    
    