from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "movies"

TECHNICAL_SPEC_FIELDS = {
    "aspect_ratio": "Aspect ratio",
    "visual_texture": "Visual texture",
    "sound_world": "Sound world",
    "format": "Format",
    "camera_lens": "Camera/lens",
    "technical_notes": "Technical notes",
}


def main() -> None:
    args = _parse_args()

    title = args.title or _prompt_required("Title")
    year = args.year or _prompt_required("Year")
    slug = args.slug or _slugify(title)
    tmdb_title = args.tmdb_title or title
    enjoyment_rating = args.enjoyment_rating or _prompt_required("Enjoyment rating")
    filmmaking_rating = args.filmmaking_rating or _prompt_required("Filmmaking rating")
    teaser = args.teaser or _prompt_required("Teaser")
    specs = _prompt_specs() if args.prompt_specs else {}
    reviewed = "true" if args.reviewed else "false"

    path = CONTENT_DIR / f"{slug}.md"
    if path.exists() and not args.force:
        raise SystemExit(f"{path} already exists. Re-run with --force to overwrite it.")

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _render_review_template(
            title=title,
            slug=slug,
            tmdb_title=tmdb_title,
            year=year,
            enjoyment_rating=enjoyment_rating,
            filmmaking_rating=filmmaking_rating,
            reviewed=reviewed,
            teaser=teaser,
            specs=specs,
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
    parser.add_argument("--teaser", help="Short homepage and hero teaser.")
    parser.add_argument("--reviewed", action="store_true", help="Mark this draft as visible on the homepage.")
    parser.add_argument(
        "--prompt-specs",
        action="store_true",
        help="Prompt for optional structured technical specs.",
    )
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


def _prompt_specs() -> dict[str, str]:
    specs = {}
    for key, label in TECHNICAL_SPEC_FIELDS.items():
        value = _prompt(label)
        if value:
            specs[key] = value
    return specs


def _render_review_template(
    *,
    title: str,
    slug: str,
    tmdb_title: str,
    year: str,
    enjoyment_rating: str,
    filmmaking_rating: str,
    reviewed: str,
    teaser: str,
    specs: dict[str, str],
) -> str:
    spec_lines = "".join(f"{key}: {value}\n" for key, value in specs.items())
    technical_footnotes = _technical_footnotes(specs)

    return f"""---
title: {title}
slug: {slug}
tmdb_title: {tmdb_title}
year: {year}
enjoyment_rating: {enjoyment_rating}
filmmaking_rating: {filmmaking_rating}
reviewed: {reviewed}
teaser: {teaser}
{spec_lines}---

## Primer

Add spoiler-light context for someone before watching.

## Technical Footnotes

{technical_footnotes}

## Review

Write the full critique here.

## Gallery

- Visual reference
- Production still idea
- Related artwork or image category
"""


def _technical_footnotes(specs: dict[str, str]) -> str:
    if not specs:
        return "- Add technical notes worth noticing before or during the watch."

    return "\n".join(f"- {TECHNICAL_SPEC_FIELDS[key]}: {value}" for key, value in specs.items())


def _slugify(value: str) -> str:
    allowed = []
    previous_dash = False
    for character in value.lower():
        if character.isalnum():
            allowed.append(character)
            previous_dash = False
        elif not previous_dash:
            allowed.append("-")
            previous_dash = True
    return "".join(allowed).strip("-")


if __name__ == "__main__":
    main()
