from __future__ import annotations

from typing import Any

SCORE_FIELDS = {
    "letterboxd_score": "Letterboxd score",
    "imdb_score": "IMDb score",
}


def slugify(value: str) -> str:
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


def render_review_template(
    *,
    title: str,
    slug: str,
    tmdb_title: str,
    year: str,
    enjoyment_rating: str = "TBD",
    filmmaking_rating: str = "TBD",
    reviewed: str = "false",
    teaser: str = "",
) -> str:

    front_matter = [
        f"title: {title}",
        f"slug: {slug}",
        f"tmdb_title: {tmdb_title}",
        f"year: {year}",
        f"enjoyment_rating: {enjoyment_rating}",
        f"filmmaking_rating: {filmmaking_rating}",
        f"reviewed: {reviewed}",
    ]
    if teaser:
        front_matter.append(f"teaser: {teaser}")


    front_matter_str = "\n".join(front_matter)

    return f"""---
{front_matter_str}
---

## Primer

Add spoiler-light context for someone before watching.

## Review

Write the full critique here.
"""


def get_weighted_score(movie_content: Any, metadata: dict[str, Any]) -> float | None:
    ratings = []
    weights = []

    # 1. Enjoyment Rating (weight: 0.4)
    try:
        if movie_content.enjoyment_rating and movie_content.enjoyment_rating.strip().upper() != "TBD":
            ratings.append(float(movie_content.enjoyment_rating))
            weights.append(0.4)
    except ValueError:
        pass

    # 2. Filmmaking Rating (weight: 0.4)
    try:
        if movie_content.filmmaking_rating and movie_content.filmmaking_rating.strip().upper() != "TBD":
            ratings.append(float(movie_content.filmmaking_rating))
            weights.append(0.4)
    except ValueError:
        pass

    # 3. IMDb Score (weight: 0.2)
    imdb_val = metadata.get("imdb_score") or movie_content.scores.get("IMDb score")
    if imdb_val:
        try:
            # e.g., "8.5/10" -> 8.5
            clean_val = str(imdb_val).split("/")[0].strip()
            ratings.append(float(clean_val))
            weights.append(0.2)
        except ValueError:
            pass

    if not ratings:
        return None

    return sum(r * w for r, w in zip(ratings, weights)) / sum(weights)

