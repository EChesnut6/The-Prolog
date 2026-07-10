from __future__ import annotations

import argparse
import builtins
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils import slugify

CONTENT_DIR = ROOT / "content" / "collections"
MOVIES_DIR = ROOT / "content" / "movies"

# Custom input function to support global q/quit to exit
def input(prompt: str = "") -> str:
    try:
        val = builtins.input(prompt)
        if val.strip().lower() in ("q", "quit"):
            print("\nGoodbye!")
            sys.exit(0)
        return val
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        sys.exit(0)


def main() -> None:
    args = _parse_args()

    title = args.title or _prompt_required("Collection Title")
    slug = args.slug or slugify(title)
    teaser = args.teaser or _prompt_required("Teaser/Short Description")

    # Load all available movie slugs for validation and auto-complete
    available_slugs = {p.stem for p in MOVIES_DIR.glob("*.md")}

    movies = []
    if args.movies:
        movies = [s.strip() for s in args.movies.split(",") if s.strip()]
        # Validate slugs
        invalid = [s for s in movies if s not in available_slugs]
        if invalid:
            print(f"Warning: The following movie slugs were not found in {MOVIES_DIR}: {', '.join(invalid)}")
    else:
        print("\nEnter movie slugs to include in this collection.")
        print("Type a slug and press Enter. Leave empty and press Enter when finished.")
        while True:
            val = input(f"Movie slug (already added: {len(movies)}): ").strip()
            if not val:
                break
            if val in available_slugs:
                movies.append(val)
                print(f"Added: {val}")
            else:
                # Find closest matches
                matches = [s for s in available_slugs if val in s]
                print(f"Slug '{val}' not found.")
                if matches:
                    print(f"Did you mean: {', '.join(matches[:5])}?")
                else:
                    print("No matches found. Please enter a valid movie slug.")

    # Write the collection markdown
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    path = CONTENT_DIR / f"{slug}.md"

    if path.exists() and not args.force:
        raise SystemExit(f"{path} already exists. Re-run with --force to overwrite it.")

    front_matter = [
        f"title: {title}",
        f"slug: {slug}",
        f"teaser: {teaser}",
        "movies:",
    ]
    for movie in movies:
        front_matter.append(f"  - {movie}")

    front_matter_str = "\n".join(front_matter)

    content = f"""---
{front_matter_str}
---

## Overview

Add the collection overview description here. Markdown is supported.
"""
    path.write_text(content, encoding="utf-8")
    print(f"\nCreated collection at {path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new movie collection draft.")
    parser.add_argument("--title", help="Collection title.")
    parser.add_argument("--slug", help="Collection slug.")
    parser.add_argument("--teaser", help="Collection teaser.")
    parser.add_argument("--movies", help="Comma-separated list of movie slugs.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing collection.")
    return parser.parse_args()


def _prompt_required(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print(f"{label} is required.")


if __name__ == "__main__":
    main()
