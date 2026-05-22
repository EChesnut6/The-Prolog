from __future__ import annotations

TECHNICAL_SPEC_FIELDS = {
    "aspect_ratio": "Aspect ratio",
    "visual_texture": "Visual texture",
    "sound_world": "Sound world",
    "format": "Format",
    "camera_lens": "Camera/lens",
    "technical_notes": "Technical notes",
}

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
    specs: dict[str, str] | None = None,
) -> str:
    if specs is None:
        specs = {}

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
    if specs:
        spec_lines = "".join(f"{key}: {value}\n" for key, value in specs.items())
        front_matter.append(spec_lines.rstrip())

    front_matter_str = "\n".join(front_matter)

    if not specs:
        technical_footnotes = "- Add technical notes worth noticing before or during the watch."
    else:
        technical_footnotes = "\n".join(
            f"- {TECHNICAL_SPEC_FIELDS[key]}: {value}" for key, value in specs.items()
        )

    return f"""---
{front_matter_str}
---

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
