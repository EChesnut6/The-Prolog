from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

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

    index = render_index(base_template, index_template, movies)
    (output_dir / "index.html").write_text(index, encoding="utf-8")


def render_movie(
    base_template: str,
    movie_template: str,
    movie: MovieContent,
    metadata: dict[str, str],
) -> str:
    movie_data = asdict(movie)
    movie_data.update(
        {
            "poster_url": metadata.get("poster_url", "../assets/placeholders/poster-placeholder.svg"),
            "release_date": metadata.get("release_date", movie.year),
            "director": metadata.get("director", "Director unavailable"),
            "technical_footnotes": _render_list(movie.technical_footnotes),
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


def render_index(base_template: str, index_template: str, movies: list[MovieContent]) -> str:
    movie_cards = "\n".join(_render_movie_card(movie) for movie in movies)
    content = index_template.format(movie_cards=movie_cards)
    return _wrap_page(base_template, title="The Prolog", content=content, css_path="styles.css", home_path="index.html")


def _wrap_page(base_template: str, title: str, content: str, css_path: str, home_path: str) -> str:
    return base_template.format(title=title, content=content, css_path=css_path, home_path=home_path)


def _render_movie_card(movie: MovieContent) -> str:
    return f"""
<article class="movie-card">
  <a href="reviews/{movie.slug}.html">
    <span class="movie-card__kicker">Vibe {movie.vibe}/10</span>
    <h2>{movie.title}</h2>
    <p class="movie-card__meta">{movie.year}</p>
    <p>{movie.teaser}</p>
  </a>
</article>
""".strip()


def _render_list(items: list[str]) -> str:
    if not items:
        return "<li>Details forthcoming.</li>"
    return "\n".join(f"<li>{item}</li>" for item in items)


def _read_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")
