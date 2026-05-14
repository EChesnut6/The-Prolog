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
    root_index: Path,
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
    root_index.write_text(index, encoding="utf-8")


def render_movie(
    base_template: str,
    movie_template: str,
    movie: MovieContent,
    metadata: dict[str, Any],
) -> str:
    metadata = {**metadata, **_score_metadata(movie)}
    movie_data = asdict(movie)
    for key in ("title", "year", "enjoyment_rating", "filmmaking_rating", "teaser"):
        movie_data[key] = escape(str(movie_data[key]))
    movie_data.update(
        {
            "poster_url": escape(str(metadata.get("poster_url", "../assets/placeholders/poster-placeholder.svg"))),
            "release_date": escape(str(metadata.get("release_date", movie.year))),
            "director": escape(str(metadata.get("director", "Director unavailable"))),
            "movie_badges": _render_movie_badges(movie),
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
        home_path="../../index.html",
    )


def render_index(
    base_template: str,
    index_template: str,
    movies: list[MovieContent],
    metadata_by_slug: dict[str, dict[str, Any]],
) -> str:
    movie_cards = "\n".join(_render_movie_card(movie, metadata_by_slug.get(movie.slug, {})) for movie in movies)
    reviewed_count = sum(1 for movie in movies if movie.reviewed)
    content = index_template.format(
        movie_cards=movie_cards,
        reviewed_count=reviewed_count,
        total_count=len(movies),
    )
    return _wrap_page(base_template, title="The Prolog", content=content, css_path="public/styles.css", home_path="index.html")


def _wrap_page(base_template: str, title: str, content: str, css_path: str, home_path: str) -> str:
    return base_template.format(title=title, content=content, css_path=css_path, home_path=home_path)


def _render_movie_card(movie: MovieContent, metadata: dict[str, Any]) -> str:
    metadata = {**metadata, **_score_metadata(movie)}
    poster_url = escape(str(metadata.get("poster_url") or "assets/placeholders/poster-placeholder.svg"))
    director = escape(str(metadata.get("director") or "Director unavailable"))
    title = escape(movie.title)
    teaser = _card_teaser(movie)
    year = escape(movie.year)
    kicker = _card_kicker(movie)
    reviewed = "true" if movie.reviewed else "false"
    status = "Reviewed" if movie.reviewed else "Template"
    hidden = "" if movie.reviewed else " hidden"
    director_raw = str(metadata.get("director", ""))
    keywords = " ".join(_search_keywords(movie, metadata))
    title_search = escape(movie.title.lower())
    director_search = escape(director_raw.lower())
    year_search = escape(movie.year.lower())
    keyword_search = escape(keywords.lower())
    return f"""
<article class="movie-card" data-reviewed="{reviewed}" data-title="{title_search}" data-director="{director_search}" data-year="{year_search}" data-keywords="{keyword_search}"{hidden}>
  <a href="public/reviews/{movie.slug}.html">
    <img class="movie-card__poster" src="{poster_url}" alt="{title} poster">
    <div class="movie-card__copy">
      <span class="movie-card__kicker">{kicker}</span>
      <h2>{title}</h2>
      <p class="movie-card__meta">{year} · Directed by {director}</p>
      <p class="movie-card__status">{status}</p>
      <p>{teaser}</p>
    </div>
  </a>
</article>
""".strip()


def _score_metadata(movie: MovieContent) -> dict[str, str]:
    reverse_labels = {
        "Letterboxd score": "letterboxd_score",
        "IMDb score": "imdb_score",
    }
    return {
        reverse_labels[label]: value
        for label, value in movie.scores.items()
        if label in reverse_labels
    }


def _search_keywords(movie: MovieContent, metadata: dict[str, Any]) -> list[str]:
    genres = metadata.get("genres", [])
    genre_text = " ".join(str(genre) for genre in genres) if isinstance(genres, list) else str(genres)
    return [movie.teaser, genre_text]


def _card_kicker(movie: MovieContent) -> str:
    if movie.reviewed:
        ratings = _rating_summary(movie)
        if ratings:
            return ratings
    return "Pre-flight template"


def _card_teaser(movie: MovieContent) -> str:
    if movie.letterboxd_rank and movie.teaser.startswith("Draft review template"):
        return "Primer and review draft ready for this ranked title."
    return escape(movie.teaser)


def _render_movie_badges(movie: MovieContent) -> str:
    badges = []
    if movie.enjoyment_rating and movie.enjoyment_rating.upper() != "TBD":
        badges.append(
            f"""
<div class="rating-check" aria-label="Enjoyment rating {escape(movie.enjoyment_rating)} out of 10">
  <span>Enjoyment</span>
  <strong>{escape(movie.enjoyment_rating)}/10</strong>
</div>
""".strip()
        )
    if movie.filmmaking_rating and movie.filmmaking_rating.upper() != "TBD":
        badges.append(
            f"""
<div class="rating-check" aria-label="Filmmaking rating {escape(movie.filmmaking_rating)} out of 10">
  <span>Filmmaking</span>
  <strong>{escape(movie.filmmaking_rating)}/10</strong>
</div>
""".strip()
        )
    return "\n".join(badges)


def _rating_summary(movie: MovieContent) -> str:
    ratings = []
    if movie.enjoyment_rating and movie.enjoyment_rating.upper() != "TBD":
        ratings.append(f"Enjoyment {escape(movie.enjoyment_rating)}/10")
    if movie.filmmaking_rating and movie.filmmaking_rating.upper() != "TBD":
        ratings.append(f"Filmmaking {escape(movie.filmmaking_rating)}/10")
    return " · ".join(ratings)


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
    rating = _rating_detail(metadata)
    if rating:
        details.append(rating)
    return _render_definition_list(details)


def _rating_detail(metadata: dict[str, Any]) -> tuple[str, str] | None:
    if metadata.get("letterboxd_score"):
        return ("Letterboxd score", str(metadata["letterboxd_score"]))
    if metadata.get("imdb_score"):
        return ("IMDb score", str(metadata["imdb_score"]))
    if metadata.get("vote_average"):
        return ("TMDB rating", f"{float(metadata['vote_average']):.1f}/10")
    return None


def _render_specs(specs: dict[str, str]) -> str:
    if not specs:
        return ""
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
