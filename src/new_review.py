from __future__ import annotations

import argparse
from pathlib import Path

from utils import slugify, render_review_template


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "movies"




def main() -> None:
    args = _parse_args()

    title = args.title or _prompt_required("Title")
    year = args.year or _prompt_required("Year")
    slug = args.slug or slugify(title)
    tmdb_title = args.tmdb_title or title
    enjoyment_rating = args.enjoyment_rating or _prompt_required("Enjoyment rating")
    filmmaking_rating = args.filmmaking_rating or _prompt_required("Filmmaking rating")
    reviewed = "true" if args.reviewed else "false"

    path = CONTENT_DIR / f"{slug}.md"
    if path.exists() and not args.force:
        raise SystemExit(f"{path} already exists. Re-run with --force to overwrite it.")

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_review_template(
            title=title,
            slug=slug,
            tmdb_title=tmdb_title,
            year=year,
            enjoyment_rating=enjoyment_rating,
            filmmaking_rating=filmmaking_rating,
            reviewed=reviewed,
        ),
        encoding="utf-8",
    )
    print(f"Created {path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new movie review Markdown draft.")
    parser.add_argument("--title", help="Movie title.")
    parser.add_argument("--year", help="Release year.")
    parser.add_argument("--slug", help="Review slug and Markdown filename.")
    parser.add_argument("--tmdb-title", help="TMDB search title. Defaults to --title.")
    parser.add_argument("--enjoyment-rating", help="Enjoyment/fun rating to display on the site.")
    parser.add_argument("--filmmaking-rating", help="Filmmaking quality rating to display on the site.")
    parser.add_argument("--reviewed", action="store_true", help="Mark this draft as visible on the homepage.")

    parser.add_argument("--force", action="store_true", help="Overwrite an existing draft with the same slug.")
    return parser.parse_args()


def _prompt_required(label: str) -> str:
    while True:
        value = _prompt(label)
        if value:
            return value
        print(f"{label} is required.")


def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default








if __name__ == "__main__":
    main()
