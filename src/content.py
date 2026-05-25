from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import markdown

from src.utils import slugify, SCORE_FIELDS


@dataclass(frozen=True)
class MovieContent:
    title: str
    slug: str
    tmdb_title: str
    year: str
    enjoyment_rating: str
    filmmaking_rating: str
    tagline: str
    reviewed: bool
    letterboxd_rank: str
    letterboxd_source: str
    primer: str
    scores: dict[str, str]
    review: str
    source_hash: str
    last_modified: float
    writer: str
    cast: list[str]


def load_movies(content_dir: Path) -> list[MovieContent]:
    movies = [load_movie(path) for path in content_dir.glob("*.md")]
    return sorted(
        movies,
        key=lambda movie: (not movie.reviewed, -movie.last_modified, movie.title.lower()),
    )


def load_movie(path: Path) -> MovieContent:
    raw = path.read_text(encoding="utf-8")
    metadata, body = _split_front_matter(raw, path)
    sections = _split_sections(body)

    title = metadata.get("title", path.stem.replace("-", " ").title())
    slug = metadata.get("slug", slugify(title))

    return MovieContent(
        title=title,
        slug=slug,
        tmdb_title=metadata.get("tmdb_title", title),
        year=metadata.get("year", ""),
        enjoyment_rating=metadata.get("enjoyment_rating", ""),
        filmmaking_rating=metadata.get("filmmaking_rating", ""),
        tagline=metadata.get("tagline", ""),
        reviewed=_reviewed(metadata, sections),
        letterboxd_rank=metadata.get("letterboxd_rank", ""),
        letterboxd_source=metadata.get("letterboxd_source", ""),
        primer=markdown.markdown(sections.get("Primer", "")),
        scores=_scores(metadata),
        review=markdown.markdown(sections.get("Review", "")),
        source_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        last_modified=path.stat().st_mtime,
        writer=metadata.get("writer", ""),
        cast=[c.strip() for c in metadata.get("cast", "").split(",") if c.strip()] if metadata.get("cast") else [],
    )


def _split_front_matter(raw: str, path: Path) -> tuple[dict[str, str], str]:
    if not raw.startswith("---\n"):
        raise ValueError(f"{path} must start with front matter delimited by ---")

    try:
        _, front_matter, body = raw.split("---", 2)
    except ValueError as exc:
        raise ValueError(f"{path} has incomplete front matter") from exc

    metadata: dict[str, str] = {}
    for line in front_matter.splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"{path} has invalid front matter line: {line}")
        metadata[key.strip()] = value.strip()

    return metadata, body.strip()


def _split_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = ""

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current = stripped.removeprefix("## ").strip()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)

    return {heading: "\n".join(lines).strip() for heading, lines in sections.items()}


def _markdown_list(md_text: str) -> list[str]:
    items: list[str] = []
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            # Convert inline markdown within list items
            items.append(markdown.markdown(stripped[2:]).removeprefix("<p>").removesuffix("</p>"))
    return items



def _scores(metadata: dict[str, str]) -> dict[str, str]:
    return {
        label: metadata[key]
        for key, label in SCORE_FIELDS.items()
        if metadata.get(key)
    }


def _reviewed(metadata: dict[str, str], sections: dict[str, str]) -> bool:
    # Explicit override takes precedence
    if "reviewed" in metadata:
        return metadata["reviewed"].strip().lower() in {"1", "true", "yes", "y"}

    template_markers = (
        "Draft review template",
        "Draft pre-flight checklist template",
        "Add spoiler-light context",
        "Write the full critique here.",
    )
    content = "\n".join(
        [
            metadata.get("teaser", ""),
            sections.get("Primer", ""),
            sections.get("Review", ""),
        ]
    )
    return not any(marker in content for marker in template_markers)



