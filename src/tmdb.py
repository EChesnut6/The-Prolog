from __future__ import annotations

import os
from typing import Any

try:
    import requests
except ImportError:
    requests = None

from dotenv import load_dotenv

# Load once at module level
load_dotenv()

TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w780"
OMDB_API_BASE = "https://www.omdbapi.com/"


def fetch_movie_metadata(title: str, year: str = "") -> dict[str, str | list[str] | float | int]:
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key or requests is None:
        return {}

    # Sanitize title for TMDB search: colons often cause lookup failures
    search_title = title.replace(":", "")
    movie = _search_movie(api_key, search_title, year)
    if not movie:
        return {}

    details = _movie_details(api_key, movie["id"])
    poster_path = movie.get("poster_path") or details.get("poster_path") or ""
    imdb_id = details.get("external_ids", {}).get("imdb_id", "")
    imdb_score = _imdb_score(imdb_id)

    return {
        "tmdb_id": movie["id"],
        "imdb_id": imdb_id,
        "imdb_score": imdb_score,
        "poster_url": f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else "",
        "backdrop_url": f"https://image.tmdb.org/t/p/w1280{movie.get('backdrop_path')}" if movie.get("backdrop_path") else "",
        "release_date": movie.get("release_date", "") or details.get("release_date", ""),
        "director": _director_from_details(details),
        "runtime": details.get("runtime", ""),
        "genres": [genre["name"] for genre in details.get("genres", []) if genre.get("name")],
        "vote_average": details.get("vote_average", ""),
        "tagline": details.get("tagline", ""),
    }


def _search_movie(api_key: str, title: str, year: str) -> dict[str, Any]:
    params = {"api_key": api_key, "query": title}
    if year:
        params["year"] = year

    response = requests.get(f"{TMDB_API_BASE}/search/movie", params=params, timeout=10)
    if response.status_code == 429:
        print("TMDB rate limit hit. Sleeping...")
        import time
        time.sleep(1)
        return _search_movie(api_key, title, year)
    
    response.raise_for_status()
    try:
        results = response.json().get("results", [])
    except Exception as exc:
        print(f"Failed to parse TMDB search response for '{title}': {exc}")
        return {}
        
    return results[0] if (results and results[0] is not None) else {}


def _movie_details(api_key: str, movie_id: int) -> dict[str, Any]:
    response = requests.get(
        f"{TMDB_API_BASE}/movie/{movie_id}",
        params={"api_key": api_key, "append_to_response": "credits,external_ids"},
        timeout=10,
    )
    if response.status_code == 429:
        print("TMDB rate limit hit. Sleeping...")
        import time
        time.sleep(1)
        return _movie_details(api_key, movie_id)
        
    response.raise_for_status()
    try:
        return response.json()
    except Exception as exc:
        print(f"Failed to parse TMDB details response for ID {movie_id}: {exc}")
        return {}


def _director_from_details(details: dict[str, Any]) -> str:
    crew = details.get("credits", {}).get("crew", [])
    directors = [person["name"] for person in crew if person.get("job") == "Director"]
    return ", ".join(directors)


def _imdb_score(imdb_id: str) -> str:
    omdb_key = os.getenv("OMDB_API_KEY")
    if not omdb_key or not imdb_id or requests is None:
        return ""

    try:
        response = requests.get(OMDB_API_BASE, params={"apikey": omdb_key, "i": imdb_id}, timeout=10)
        response.raise_for_status()
        rating = response.json().get("imdbRating", "")
        return f"{rating}/10" if rating and rating != "N/A" else ""
    except Exception as exc:
        print(f"OMDB lookup failed for IMDB ID {imdb_id}: {exc}")
        return ""
