from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.content import load_movies, load_collections, load_articles
from src.metadata_cache import (
    cache_entry_is_fresh,
    load_metadata_cache,
    make_cache_entry,
    save_metadata_cache,
    load_directors_cache,
    save_directors_cache,
)
from src.render import render_site
from src.tmdb import fetch_movie_metadata, fetch_person_metadata
from src.utils import slugify


CONTENT_DIR = ROOT / "content" / "movies"
COLLECTIONS_DIR = ROOT / "content" / "collections"
ARTICLES_DIR = ROOT / "content" / "articles"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "public"
ROOT_INDEX = ROOT / "index.html"
ROOT_SEARCH = OUTPUT_DIR / "search.html"
ASSETS_DIR = ROOT / "assets"
METADATA_CACHE = ROOT / ".tmdb-cache.json"


def main() -> None:
    args = _parse_args()
    movies = load_movies(CONTENT_DIR)
    collections = load_collections(COLLECTIONS_DIR)
    articles = load_articles(ARTICLES_DIR)
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

    # Load director cache
    directors_cache_path = ROOT / ".tmdb-directors-cache.json"
    directors_cache = load_directors_cache(directors_cache_path)
    directors_metadata = {}
    directors_cache_changed = False

    # Extract unique directors
    unique_directors = set()
    for slug, meta in metadata_by_slug.items():
        if meta and "director" in meta:
            dir_val = meta["director"]
            if dir_val and dir_val != "Director unavailable":
                for d in dir_val.split(","):
                    d_clean = d.strip()
                    if d_clean:
                        unique_directors.add(d_clean)

    for d_name in sorted(unique_directors):
        d_slug = slugify(d_name)
        cached_entry = directors_cache.get(d_slug, {})
        use_dir_cache = cached_entry and not args.refresh_metadata
        if use_dir_cache:
            directors_metadata[d_slug] = cached_entry
            continue

        try:
            print(f"Fetching TMDB director details for: {d_name}")
            dir_meta = fetch_person_metadata(d_name)
            if dir_meta:
                directors_cache[d_slug] = dir_meta
                directors_metadata[d_slug] = dir_meta
                directors_cache_changed = True
            else:
                directors_metadata[d_slug] = cached_entry or {"name": d_name}
        except Exception as exc:
            print(f"TMDB director details fetch failed for {d_name}: {exc}")
            directors_metadata[d_slug] = cached_entry or {"name": d_name}

    if directors_cache_changed:
        save_directors_cache(directors_cache_path, directors_cache)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _copy_assets()
    render_site(movies, metadata_by_slug, collections, articles, directors_metadata, TEMPLATES_DIR, OUTPUT_DIR, ROOT_INDEX, ROOT_SEARCH)
    print(f"Built {len(movies)} movie page(s), {len(unique_directors)} director page(s), {len(collections)} collection page(s), and {len(articles)} article page(s) in {OUTPUT_DIR} and {ROOT_INDEX}")


def _copy_assets() -> None:
    source = ASSETS_DIR
    destination = OUTPUT_DIR / "assets"
    if source.exists():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    
    favicon_src = ROOT / "favicon.png"
    favicon_dst = OUTPUT_DIR / "favicon.png"
    if favicon_src.exists():
        shutil.copy2(favicon_src, favicon_dst)



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
