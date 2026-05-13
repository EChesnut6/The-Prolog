from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.content import load_movies
from src.render import render_site
from src.tmdb import fetch_movie_metadata


CONTENT_DIR = ROOT / "content" / "movies"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "public"
ASSETS_DIR = ROOT / "assets"


def main() -> None:
    movies = load_movies(CONTENT_DIR)
    metadata_by_slug = {}

    for movie in movies:
        try:
            metadata_by_slug[movie.slug] = fetch_movie_metadata(movie.tmdb_title, movie.year)
        except Exception as exc:
            print(f"TMDB lookup failed for {movie.title}: {exc}")
            metadata_by_slug[movie.slug] = {}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _copy_assets()
    render_site(movies, metadata_by_slug, TEMPLATES_DIR, OUTPUT_DIR)
    print(f"Built {len(movies)} movie page(s) in {OUTPUT_DIR}")


def _copy_assets() -> None:
    source = ASSETS_DIR
    destination = OUTPUT_DIR / "assets"
    if source.exists():
        shutil.copytree(source, destination, dirs_exist_ok=True)


if __name__ == "__main__":
    main()
