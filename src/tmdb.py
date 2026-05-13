from __future__ import annotations

import os
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover - exercised only before dependencies are installed.
    requests = None

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - exercised only before dependencies are installed.
    def load_dotenv() -> None:
        return None


TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w780"


def fetch_movie_metadata(title: str, year: str = "") -> dict[str, str]:
    load_dotenv()
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key or requests is None:
        return {}

    movie = _search_movie(api_key, title, year)
    if not movie:
        return {}

    details = _movie_details(api_key, movie["id"])
    poster_path = movie.get("poster_path") or details.get("poster_path") or ""

    return {
        "poster_url": f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else "",
        "release_date": movie.get("release_date", "") or details.get("release_date", ""),
        "director": _director_from_details(details),
    }


def _search_movie(api_key: str, title: str, year: str) -> dict[str, Any]:
    params = {"api_key": api_key, "query": title}
    if year:
        params["year"] = year

    response = requests.get(f"{TMDB_API_BASE}/search/movie", params=params, timeout=10)
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[0] if results else {}


def _movie_details(api_key: str, movie_id: int) -> dict[str, Any]:
    response = requests.get(
        f"{TMDB_API_BASE}/movie/{movie_id}",
        params={"api_key": api_key, "append_to_response": "credits"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _director_from_details(details: dict[str, Any]) -> str:
    crew = details.get("credits", {}).get("crew", [])
    directors = [person["name"] for person in crew if person.get("job") == "Director"]
    return ", ".join(directors)
