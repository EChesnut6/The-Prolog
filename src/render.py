from __future__ import annotations

import random
from dataclasses import asdict
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.content import MovieContent
from src.utils import SCORE_FIELDS

import datetime


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

    movies_with_metadata = []
    for m in movies:
        meta = metadata_by_slug.get(m.slug, {})
        meta = {**meta, **_score_metadata(m)}
        movies_with_metadata.append((m, meta))

    for movie in movies:
        metadata = metadata_by_slug.get(movie.slug, {})
        page = render_movie(base_template, movie_template, movie, metadata, movies_with_metadata)
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
    all_movies: list[tuple[MovieContent, dict[str, Any]]],
) -> str:
    metadata = {**metadata, **_score_metadata(movie)}
    
    # Path logic: reviews are in public/reviews/, so they need to go up one level to see public/assets/
    # BUT if the site is served from root (like GH Pages), it depends on the URL structure.
    # Usually, public/reviews/movie.html needs "../assets/..."
    
    similar_movies = _get_similar_movies(movie, metadata, all_movies)
    
    movie_data = asdict(movie)
    movie_data.update(
        {
            "poster_url": metadata.get("poster_url") or "../assets/placeholders/poster-placeholder.svg",
            "backdrop_url": metadata.get("backdrop_url") or metadata.get("poster_url") or "../assets/placeholders/poster-placeholder.svg",
            "release_date": metadata.get("release_date") or movie.year,
            "director": metadata.get("director") or "Director unavailable",
            "writer": movie.writer or metadata.get("writer") or "N/A",
            "cast": movie.cast or metadata.get("cast") or [],
            "genres": metadata.get("genres") or [],
            "runtime": metadata.get("runtime") or "",
            "tagline": movie.tagline or metadata.get("tagline", ""),
            "metadata": metadata,
            "similar_movies": similar_movies,
        }
    )
    
    content = movie_template.render(**movie_data)
    return base_template.render(
        title=f"{movie.title} | The Prolog",
        date= datetime.date.today(),
        content=content,
        css_path="../styles.css",
        home_path="../../index.html",
        search_path="../search.html",
        coming_soon_path="../coming-soon.html",
        theme_toggle_js_path="../assets/js/theme-toggle.js",
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
        date= datetime.date.today(),
        content=content,
        css_path="public/styles.css",
        home_path="index.html",
        search_path="public/search.html",
        coming_soon_path="public/coming-soon.html",
        theme_toggle_js_path="public/assets/js/theme-toggle.js",
    )


def render_coming_soon(
    base_template: Any,
    coming_soon_template: Any,
) -> str:
    content = coming_soon_template.render(home_path="../index.html")
    return base_template.render(
        title="Coming Soon | The Prolog",
        date= datetime.date.today(),
        content=content,
        css_path="styles.css",
        home_path="../index.html",
        search_path="search.html",
        coming_soon_path="coming-soon.html",
        theme_toggle_js_path="assets/js/theme-toggle.js",
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
            "poster_url": metadata.get("poster_url") or "assets/placeholders/poster-placeholder.svg",
            "director": metadata.get("director") or "Director unavailable",
            "search_keywords": " ".join(_search_keywords(movie, metadata)).lower()
        })

    content = search_template.render(
        movie_cards=movie_cards_data,
        search_js_path="assets/js/search-controller.js"
    )
    return base_template.render(
        title="Search Movies | The Prolog",
        date= datetime.date.today(),
        content=content,
        css_path="styles.css",
        home_path="../index.html",
        search_path="search.html",
        coming_soon_path="coming-soon.html",
        theme_toggle_js_path="assets/js/theme-toggle.js",
    )


def _score_metadata(movie: MovieContent) -> dict[str, str]:
    reverse_labels = {v: k for k, v in SCORE_FIELDS.items()}
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


def _get_similar_movies(
    current_movie: MovieContent,
    current_metadata: dict[str, Any],
    all_movies: list[tuple[MovieContent, dict[str, Any]]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    scored_movies = []
    current_genres = set(current_metadata.get("genres", []))
    current_director = current_metadata.get("director", "")
    current_year = current_movie.year or current_metadata.get("release_date", "")[:4]

    for other_movie, other_metadata in all_movies:
        if other_movie.slug == current_movie.slug:
            continue
        
        score = 0
        
        # Check director match
        other_director = other_metadata.get("director", "")
        if current_director and other_director and current_director == other_director:
            score += 10
            
        # Check genre match
        other_genres = set(other_metadata.get("genres", []))
        shared_genres = current_genres.intersection(other_genres)
        score += len(shared_genres) * 3
        
        # Check era (same decade)
        other_year = other_movie.year or other_metadata.get("release_date", "")[:4]
        if current_year and other_year:
            try:
                if abs(int(current_year[:4]) - int(other_year[:4])) <= 10:
                    score += 2
            except ValueError:
                pass
                
        # Prefer reviewed movies
        if other_movie.reviewed:
            score += 5
            
        scored_movies.append((score, other_movie, other_metadata))
        
    # Sort by score descending, then by title
    scored_movies.sort(key=lambda x: (-x[0], x[1].title))
    
    similar = []
    for score, m, meta in scored_movies[:limit]:
        similar.append({
            "title": m.title,
            "slug": m.slug,
            "poster_url": meta.get("poster_url") or "../assets/placeholders/poster-placeholder.svg",
            "year": m.year or meta.get("release_date", "")[:4],
        })
        
    return similar
