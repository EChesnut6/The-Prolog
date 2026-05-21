from __future__ import annotations

import random
from dataclasses import asdict
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.content import MovieContent


def render_site(
    movies: list[MovieContent],
    metadata_by_slug: dict[str, dict[str, Any]],
    templates_dir: Path,
    output_dir: Path,
    root_index: Path,
    root_search: Path,
) -> None:
    reviews_dir = output_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    base_template = env.get_template("base.html")
    movie_template = env.get_template("movie.html")
    index_template = env.get_template("index.html")
    search_template = env.get_template("search.html")
    coming_soon_template = env.get_template("coming-soon.html")

    for movie in movies:
        metadata = metadata_by_slug.get(movie.slug, {})
        page = render_movie(base_template, movie_template, movie, metadata)
        (reviews_dir / f"{movie.slug}.html").write_text(page, encoding="utf-8")

    index = render_index(base_template, index_template, movies, metadata_by_slug)
    root_index.write_text(index, encoding="utf-8")

    search_page = render_search(base_template, search_template, movies, metadata_by_slug)
    root_search.write_text(search_page, encoding="utf-8")

    coming_soon = render_coming_soon(base_template, coming_soon_template)
    (output_dir / "coming-soon.html").write_text(coming_soon, encoding="utf-8")


def render_movie(
    base_template: Any,
    movie_template: Any,
    movie: MovieContent,
    metadata: dict[str, Any],
) -> str:
    metadata = {**metadata, **_score_metadata(movie)}
    
    # Path logic: reviews are in public/reviews/, so they need to go up one level to see public/assets/
    # BUT if the site is served from root (like GH Pages), it depends on the URL structure.
    # Usually, public/reviews/movie.html needs "../assets/..."
    
    movie_data = asdict(movie)
    movie_data.update(
        {
            "poster_url": metadata.get("poster_url") or "../assets/placeholders/poster-placeholder.svg",
            "release_date": metadata.get("release_date") or movie.year,
            "director": metadata.get("director") or "Director unavailable",
            "tagline": movie.tagline or metadata.get("tagline", ""),
            "metadata": metadata,
        }
    )
    
    content = movie_template.render(**movie_data)
    return base_template.render(
        title=f"{movie.title} | The Prolog",
        content=content,
        css_path="../styles.css",
        home_path="../../index.html",
        search_path="../../search.html",
        coming_soon_path="../coming-soon.html",
    )


def render_index(
    base_template: Any,
    index_template: Any,
    movies: list[MovieContent],
    metadata_by_slug: dict[str, dict[str, Any]],
) -> str:
    reviewed_count = sum(1 for movie in movies if movie.reviewed)
    
    # Homepage is at root, so it sees public/assets/ and public/reviews/
    movie_cards_data = []
    for movie in movies:
        metadata = {**metadata_by_slug.get(movie.slug, {}), **_score_metadata(movie)}
        movie_cards_data.append({
            "movie": movie,
            "metadata": metadata,
            "poster_url": metadata.get("poster_url") or "public/assets/placeholders/poster-placeholder.svg",
            "backdrop_url": metadata.get("backdrop_url") or "",
            "director": metadata.get("director") or "Director unavailable",
            "tagline": movie.tagline or metadata.get("tagline", ""),
            "kicker": _card_kicker(movie),
            "reviewed_attr": "true" if movie.reviewed else "false",
            "status": "Reviewed" if movie.reviewed else "Template",
            "hidden_attr": "" if movie.reviewed else " hidden",
            "search_keywords": " ".join(_search_keywords(movie, metadata)).lower()
        })

    reviewed_movies = [card for card in movie_cards_data if card["movie"].reviewed]
    
    # Homepage segments
    random_teaser = random.choice(reviewed_movies) if reviewed_movies else None
    new_reviews = reviewed_movies[:4]
    latest_sidebar = reviewed_movies[:10]
    
    # "Masterpieces" (Great Movies) - filmmaking_rating >= 9
    def is_great(card):
        try:
            rating = float(card["movie"].filmmaking_rating)
            return rating >= 9
        except (ValueError, TypeError):
            return False
            
    great_movies = [card for card in reviewed_movies if is_great(card)]

    content = index_template.render(
        movie_cards=movie_cards_data,
        reviewed_count=reviewed_count,
        total_count=len(movies),
        random_teaser=random_teaser,
        new_reviews=new_reviews,
        great_movies=great_movies,
        latest_sidebar=latest_sidebar,
    )
    return base_template.render(
        title="The Prolog",
        content=content,
        css_path="public/styles.css",
        home_path="index.html",
        search_path="search.html",
        coming_soon_path="public/coming-soon.html"
    )


def render_coming_soon(
    base_template: Any,
    coming_soon_template: Any,
) -> str:
    content = coming_soon_template.render(home_path="../index.html")
    return base_template.render(
        title="Coming Soon | The Prolog",
        content=content,
        css_path="styles.css",
        home_path="../index.html",
        search_path="../search.html",
        coming_soon_path="coming-soon.html"
    )

def render_search(
    base_template: Any,
    search_template: Any,
    movies: list[MovieContent],
    metadata_by_slug: dict[str, dict[str, Any]],
) -> str:
    movie_cards_data = []
    for movie in movies:
        metadata = {**metadata_by_slug.get(movie.slug, {}), **_score_metadata(movie)}
        movie_cards_data.append({
            "movie": movie,
            "metadata": metadata,
            "poster_url": metadata.get("poster_url") or "public/assets/placeholders/poster-placeholder.svg",
            "director": metadata.get("director") or "Director unavailable",
            "search_keywords": " ".join(_search_keywords(movie, metadata)).lower()
        })

    content = search_template.render(movie_cards=movie_cards_data)
    return base_template.render(
        title="Search Movies | The Prolog",
        content=content,
        css_path="public/styles.css",
        home_path="index.html",
        search_path="search.html",
        coming_soon_path="public/coming-soon.html"
    )


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
    return [genre_text]


def _card_kicker(movie: MovieContent) -> str:
    if movie.reviewed:
        ratings = []
        if movie.enjoyment_rating and movie.enjoyment_rating.upper() != "TBD":
            ratings.append(f"Enjoyment {movie.enjoyment_rating}/10")
        if movie.filmmaking_rating and movie.filmmaking_rating.upper() != "TBD":
            ratings.append(f"Filmmaking {movie.filmmaking_rating}/10")
        return " · ".join(ratings)
    return "Pre-flight template"
