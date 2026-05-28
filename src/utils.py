from __future__ import annotations


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
