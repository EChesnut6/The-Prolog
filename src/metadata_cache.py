from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.content import MovieContent


CacheData = dict[str, dict[str, Any]]


def load_metadata_cache(path: Path) -> CacheData:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}

    movies = data.get("movies", {})
    return movies if isinstance(movies, dict) else {}


def save_metadata_cache(path: Path, cache: CacheData) -> None:
    path.write_text(
        json.dumps({"movies": cache}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def cache_entry_is_fresh(entry: dict[str, Any], movie: MovieContent) -> bool:
    return (
        entry.get("source_hash") == movie.source_hash
        and entry.get("tmdb_title") == movie.tmdb_title
        and entry.get("year") == movie.year
    )


def make_cache_entry(movie: MovieContent, metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_hash": movie.source_hash,
        "tmdb_title": movie.tmdb_title,
        "year": movie.year,
        "metadata": metadata,
    }
