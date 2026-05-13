from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MovieContent:
    title: str
    slug: str
    tmdb_title: str
    year: str
    vibe: str
    teaser: str
    primer: str
    technical_footnotes: list[str]
    review: str
    gallery: list[str]


def load_movies(content_dir: Path) -> list[MovieContent]:
    movies = [load_movie(path) for path in sorted(content_dir.glob("*.md"))]
    return sorted(movies, key=lambda movie: (movie.title.lower(), movie.year))


def load_movie(path: Path) -> MovieContent:
    raw = path.read_text(encoding="utf-8")
    metadata, body = _split_front_matter(raw, path)
    sections = _split_sections(body)

    title = metadata.get("title", path.stem.replace("-", " ").title())
    slug = metadata.get("slug", _slugify(title))

    return MovieContent(
        title=title,
        slug=slug,
        tmdb_title=metadata.get("tmdb_title", title),
        year=metadata.get("year", ""),
        vibe=metadata.get("vibe", ""),
        teaser=metadata.get("teaser", ""),
        primer=_markdown_paragraphs(sections.get("Primer", "")),
        technical_footnotes=_markdown_list(sections.get("Technical Footnotes", "")),
        review=_markdown_paragraphs(sections.get("Review", "")),
        gallery=_markdown_list(sections.get("Gallery", "")),
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
        if line.startswith("## "):
            current = line.removeprefix("## ").strip()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)

    return {heading: "\n".join(lines).strip() for heading, lines in sections.items()}


def _markdown_paragraphs(markdown: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in markdown.split("\n\n") if paragraph.strip()]
    return "\n".join(f"<p>{_inline_markdown(paragraph)}</p>" for paragraph in paragraphs)


def _markdown_list(markdown: str) -> list[str]:
    items: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(_inline_markdown(stripped[2:]))
    return items


def _inline_markdown(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


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

