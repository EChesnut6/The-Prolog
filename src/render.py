from __future__ import annotations

from dataclasses import asdict
from html import escape
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from src.content import MovieContent


def render_site(
    movies: list[MovieContent],
    metadata_by_slug: dict[str, dict[str, str]],
    templates_dir: Path,
    output_dir: Path,
) -> None:
    reviews_dir = output_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    base_template = _read_template(templates_dir / "base.html")
    movie_template = _read_template(templates_dir / "movie.html")
    index_template = _read_template(templates_dir / "index.html")

    for movie in movies:
        metadata = metadata_by_slug.get(movie.slug, {})
        page = render_movie(base_template, movie_template, movie, metadata)
        (reviews_dir / f"{movie.slug}.html").write_text(page, encoding="utf-8")

    index = render_index(base_template, index_template, movies, metadata_by_slug)
    (output_dir / "index.html").write_text(index, encoding="utf-8")


def render_movie(
    base_template: str,
    movie_template: str,
    movie: MovieContent,
    metadata: dict[str, Any],
) -> str:
    movie_data = asdict(movie)
    for key in ("title", "year", "vibe", "teaser"):
        movie_data[key] = escape(str(movie_data[key]))
    movie_data.update(
        {
            "poster_url": escape(str(metadata.get("poster_url", "../assets/placeholders/poster-placeholder.svg"))),
            "release_date": escape(str(metadata.get("release_date", movie.year))),
            "director": escape(str(metadata.get("director", "Director unavailable"))),
            "movie_details": _render_movie_details(metadata),
            "technical_footnotes": _render_list(movie.technical_footnotes),
            "technical_specs": _render_specs(movie.technical_specs),
            "gallery": _render_list(movie.gallery),
        }
    )
    content = movie_template.format(**movie_data)
    return _wrap_page(
        base_template,
        title=f"{movie.title} | The Prolog",
        content=content,
        css_path="../styles.css",
        home_path="../index.html",
    )


def render_index(
    base_template: str,
    index_template: str,
    movies: list[MovieContent],
    metadata_by_slug: dict[str, dict[str, Any]],
) -> str:
    movie_cards = "\n".join(_render_movie_card(movie, metadata_by_slug.get(movie.slug, {})) for movie in movies)
    content = index_template.format(movie_cards=movie_cards)
    return _wrap_page(base_template, title="The Prolog", content=content, css_path="styles.css", home_path="index.html")


def _wrap_page(base_template: str, title: str, content: str, css_path: str, home_path: str) -> str:
    return base_template.format(title=title, content=content, css_path=css_path, home_path=home_path)


def _render_movie_card(movie: MovieContent, metadata: dict[str, Any]) -> str:
    poster_url = escape(str(metadata.get("poster_url") or "assets/placeholders/poster-placeholder.svg"))
    director = escape(str(metadata.get("director") or "Director unavailable"))
    title = escape(movie.title)
    teaser = escape(movie.teaser)
    year = escape(movie.year)
    vibe = escape(movie.vibe)
    return f"""
<article class="movie-card">
  <a href="reviews/{movie.slug}.html">
    <img class="movie-card__poster" src="{poster_url}" alt="{title} poster">
    <div class="movie-card__copy">
      <span class="movie-card__kicker">Vibe {vibe}/10</span>
      <h2>{title}</h2>
      <p class="movie-card__meta">{year} · Directed by {director}</p>
      <p>{teaser}</p>
    </div>
  </a>
</article>
""".strip()


def _render_list(items: list[str]) -> str:
    if not items:
        return "<li>Details forthcoming.</li>"
    return "\n".join(f"<li>{item}</li>" for item in items)


def _render_movie_details(metadata: dict[str, Any]) -> str:
    details = []
    if metadata.get("runtime"):
        details.append(("Runtime", f"{metadata['runtime']} min"))
    if metadata.get("genres"):
        details.append(("Genres", ", ".join(str(genre) for genre in metadata["genres"])))
    if metadata.get("vote_average"):
        details.append(("TMDB rating", f"{float(metadata['vote_average']):.1f}/10"))
    if metadata.get("tmdb_id"):
        details.append(("TMDB id", str(metadata["tmdb_id"])))
    return _render_definition_list(details)


def _render_specs(specs: dict[str, str]) -> str:
    return _render_definition_list(specs.items())


def _render_definition_list(items: Iterable[tuple[Any, Any]]) -> str:
    rendered = []
    for label, value in items:
        if value:
            rendered.append(f"<dt>{escape(str(label))}</dt><dd>{escape(str(value))}</dd>")
    if not rendered:
        return "<p class=\"empty-note\">Details forthcoming.</p>"
    return "<dl>\n" + "\n".join(rendered) + "\n</dl>"


def _read_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")
