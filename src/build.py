from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.content import load_movies
from src.metadata_cache import (
    cache_entry_is_fresh,
    load_metadata_cache,
    make_cache_entry,
    save_metadata_cache,
)
from src.render import render_site
from src.tmdb import fetch_movie_metadata


CONTENT_DIR = ROOT / "content" / "movies"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "public"
ROOT_INDEX = ROOT / "index.html"
ROOT_SEARCH = ROOT / "search.html"
ASSETS_DIR = ROOT / "assets"
METADATA_CACHE = ROOT / ".tmdb-cache.json"


def main() -> None:
    args = _parse_args()
    movies = load_movies(CONTENT_DIR)
    cache_path = args.metadata_cache
    cache = load_metadata_cache(cache_path)
    metadata_by_slug = {}
    cache_changed = False

    for movie in movies:
        entry = cache.get(movie.slug, {})
        cached_metadata = entry.get("metadata", {}) if isinstance(entry, dict) else {}
        use_cache = cached_metadata and not args.refresh_metadata and cache_entry_is_fresh(entry, movie)

        if use_cache:
            metadata_by_slug[movie.slug] = cached_metadata
            continue

        try:
            metadata = fetch_movie_metadata(movie.tmdb_title, movie.year)
            if metadata:
                cache[movie.slug] = make_cache_entry(movie, metadata)
                cache_changed = True
            elif cached_metadata:
                metadata = cached_metadata
            metadata_by_slug[movie.slug] = metadata
        except Exception as exc:
            print(f"TMDB lookup failed for {movie.title}: {exc}")
            metadata_by_slug[movie.slug] = cached_metadata or {}

    if cache_changed:
        save_metadata_cache(cache_path, cache)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _copy_assets()
    render_site(movies, metadata_by_slug, TEMPLATES_DIR, OUTPUT_DIR, ROOT_INDEX, ROOT_SEARCH)
    print(f"Built {len(movies)} movie page(s) in {OUTPUT_DIR} and {ROOT_INDEX}")


def _copy_assets() -> None:
    source = ASSETS_DIR
    destination = OUTPUT_DIR / "assets"
    if source.exists():
        shutil.copytree(source, destination, dirs_exist_ok=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build The Prolog static site.")
    parser.add_argument(
        "--refresh-metadata",
        action="store_true",
        help="Refresh TMDB metadata instead of using fresh cache entries.",
    )
    parser.add_argument(
        "--metadata-cache",
        type=Path,
        default=METADATA_CACHE,
        help="Path to the TMDB metadata cache JSON file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
