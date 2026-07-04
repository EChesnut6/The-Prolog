from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import markdown

import re

from src.utils import slugify, SCORE_FIELDS


def convert_wiki_links(text: str) -> str:
    # Pattern to match [[target]] or [[target|anchor]]
    pattern = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    
    def replace(match):
        target = match.group(1).strip()
        anchor = match.group(2)
        
        # If target has a file extension, strip it
        clean_target = target.removesuffix(".md").removesuffix(".html")
        slug = slugify(clean_target)
        
        if anchor is not None:
            anchor_text = anchor.strip()
        else:
            anchor_text = target
            
        return f"[{anchor_text}]({slug}.md)"
        
    return pattern.sub(replace, text)


def _extract_premise_section(primer_text: str) -> str | None:
    lines = primer_text.splitlines()
    premise_lines = []
    in_premise = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            if "premise" in stripped.lower():
                in_premise = True
                premise_lines.append(line)
            elif in_premise:
                break
        else:
            if in_premise:
                premise_lines.append(line)
                
    if premise_lines:
        return "\n".join(premise_lines).strip()
    return None


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
    premise: str | None


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

    primer_text = convert_wiki_links(sections.get("Primer", ""))
    review_text = convert_wiki_links(sections.get("Review", ""))
    premise_raw = _extract_premise_section(primer_text)

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
        primer=markdown.markdown(primer_text),
        scores=_scores(metadata),
        review=markdown.markdown(review_text),
        source_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        last_modified=path.stat().st_mtime,
        writer=metadata.get("writer", ""),
        cast=[c.strip() for c in metadata.get("cast", "").split(",") if c.strip()] if metadata.get("cast") else [],
        premise=markdown.markdown(premise_raw) if premise_raw else None,
    )


def _split_front_matter(raw: str, path: Path) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---\n"):
        raise ValueError(f"{path} must start with front matter delimited by ---")

    try:
        _, front_matter, body = raw.split("---", 2)
    except ValueError as exc:
        raise ValueError(f"{path} has incomplete front matter") from exc

    metadata: dict[str, Any] = {}
    current_key = None
    for line in front_matter.splitlines():
        if not line.strip():
            continue
        # Support list items under a key
        if line.strip().startswith("-") and current_key:
            val = line.strip().lstrip("-").strip()
            if not isinstance(metadata[current_key], list):
                metadata[current_key] = []
            metadata[current_key].append(val)
            continue

        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"{path} has invalid front matter line: {line}")
        
        key_str = key.strip()
        val_str = value.strip()
        
        if not val_str:
            metadata[key_str] = []
            current_key = key_str
        else:
            metadata[key_str] = val_str
            current_key = key_str

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



@dataclass(frozen=True)
class CollectionContent:
    title: str
    slug: str
    teaser: str
    movies: list[str]
    overview: str


def load_collections(content_dir: Path) -> list[CollectionContent]:
    if not content_dir.exists():
        return []
    collections = [load_collection(path) for path in content_dir.glob("*.md")]
    return sorted(collections, key=lambda col: col.title.lower())


def load_collection(path: Path) -> CollectionContent:
    raw = path.read_text(encoding="utf-8")
    metadata, body = _split_front_matter(raw, path)

    title = metadata.get("title", path.stem.replace("-", " ").title())
    slug = metadata.get("slug", slugify(title))
    teaser = metadata.get("teaser", "")
    movies = metadata.get("movies", [])
    if isinstance(movies, str):
        movies = [s.strip() for s in movies.split(",") if s.strip()]

    overview_text = convert_wiki_links(body)
    overview = markdown.markdown(overview_text)

    return CollectionContent(
        title=title,
        slug=slug,
        teaser=teaser,
        movies=movies,
        overview=overview,
    )


@dataclass(frozen=True)
class ArticleContent:
    title: str
    slug: str
    teaser: str
    author: str
    date: str
    body: str
    source_hash: str
    last_modified: float


def load_articles(content_dir: Path) -> list[ArticleContent]:
    if not content_dir.exists():
        return []
    articles = [load_article(path) for path in content_dir.glob("*.md")]
    return sorted(
        articles,
        key=lambda art: (art.date or "", -art.last_modified, art.title.lower()),
        reverse=True
    )


def load_article(path: Path) -> ArticleContent:
    raw = path.read_text(encoding="utf-8")
    metadata, body = _split_front_matter(raw, path)

    title = metadata.get("title", path.stem.replace("-", " ").title())
    slug = metadata.get("slug", slugify(title))
    teaser = metadata.get("teaser", "")
    author = metadata.get("author", metadata.get("writer", "Eli Chesnut"))
    date_str = metadata.get("date", "")

    body_text = convert_wiki_links(body)
    body_html = markdown.markdown(body_text)

    return ArticleContent(
        title=title,
        slug=slug,
        teaser=teaser,
        author=author,
        date=str(date_str),
        body=body_html,
        source_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        last_modified=path.stat().st_mtime,
    )

