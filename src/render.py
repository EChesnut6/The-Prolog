from __future__ import annotations

import random
from dataclasses import asdict
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.content import MovieContent, CollectionContent, ArticleContent
from src.utils import SCORE_FIELDS, get_weighted_score

import datetime
import re


def resolve_links(html: str, page_type: str, all_movie_slugs: set[str], all_article_slugs: set[str]) -> str:
    # Prefix mapping for valid reviews
    review_prefixes = {
        "root": "public/reviews/",
        "public": "reviews/",
        "review": "",
        "collection": "../reviews/",
        "article": "../reviews/"
    }
    
    # Prefix mapping for valid articles
    article_prefixes = {
        "root": "public/articles/",
        "public": "articles/",
        "review": "../articles/",
        "collection": "../articles/",
        "article": ""
    }
    
    # Prefix mapping for coming soon page (when movie is missing/draft that isn't built)
    coming_soon_paths = {
        "root": "public/coming-soon.html",
        "public": "coming-soon.html",
        "review": "../coming-soon.html",
        "collection": "../coming-soon.html",
        "article": "../coming-soon.html"
    }
    
    review_prefix = review_prefixes.get(page_type, "")
    article_prefix = article_prefixes.get(page_type, "")
    coming_soon_path = coming_soon_paths.get(page_type, "coming-soon.html")
    
    # Matches href="movie-slug.md" or href="./movie-slug.md"
    pattern = r'href="(?:\./)?([^/"]+)\.md"'
    
    def replace_link(match):
        slug = match.group(1)
        if slug in all_movie_slugs:
            return f'href="{review_prefix}{slug}.html"'
        elif slug in all_article_slugs:
            return f'href="{article_prefix}{slug}.html"'
        else:
            return f'href="{coming_soon_path}"'
            
    return re.sub(pattern, replace_link, html)


def render_site(
    movies: list[MovieContent],
    metadata_by_slug: dict[str, dict[str, Any]],
    collections: list[CollectionContent],
    articles: list[ArticleContent],
    templates_dir: Path,
    output_dir: Path,
    root_index: Path,
    root_search: Path,
) -> None:
    reviews_dir = output_dir / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    collections_dir = output_dir / "collections"
    collections_dir.mkdir(parents=True, exist_ok=True)

    articles_dir = output_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    base_template = env.get_template("base.html")
    movie_template = env.get_template("movie.html")
    index_template = env.get_template("index.html")
    search_template = env.get_template("search.html")
    coming_soon_template = env.get_template("coming-soon.html")
    greats_template = env.get_template("greats.html")
    collections_index_template = env.get_template("collections_index.html")
    collection_detail_template = env.get_template("collection_detail.html")
    articles_template = env.get_template("articles.html")
    article_template = env.get_template("article.html")

    movies_with_metadata = []
    for m in movies:
        meta = metadata_by_slug.get(m.slug, {})
        meta = {**meta, **_score_metadata(m)}
        movies_with_metadata.append((m, meta))

    # Calculate great movies based on weighted average of scores
    great_movies = []
    for movie in movies:
        if not movie.reviewed:
            continue
        metadata = metadata_by_slug.get(movie.slug, {})
        metadata = {**metadata, **_score_metadata(movie)}
        score = get_weighted_score(movie, metadata)
        if score is not None and score >= 8.5:
            great_movies.append({
                "movie": movie,
                "metadata": metadata,
                "weighted_score": round(score, 2),
                "poster_url": metadata.get("poster_url") or "public/assets/placeholders/poster-placeholder.svg",
                "director": metadata.get("director") or "Director unavailable",
                "tagline": movie.tagline or metadata.get("tagline", ""),
            })
    great_movies.sort(key=lambda x: (-x["weighted_score"], x["movie"].title.lower()))

    # Render movie pages
    all_movie_slugs = {m.slug for m in movies}
    all_article_slugs = {a.slug for a in articles}
    
    for movie in movies:
        metadata = metadata_by_slug.get(movie.slug, {})
        page = render_movie(base_template, movie_template, movie, metadata, movies_with_metadata)
        page = resolve_links(page, "review", all_movie_slugs, all_article_slugs)
        (reviews_dir / f"{movie.slug}.html").write_text(page, encoding="utf-8")

    # Render articles pages
    for article in articles:
        page = render_article(base_template, article_template, article)
        page = resolve_links(page, "article", all_movie_slugs, all_article_slugs)
        (articles_dir / f"{article.slug}.html").write_text(page, encoding="utf-8")

    # Render index
    index = render_index(base_template, index_template, movies, metadata_by_slug, collections, great_movies)
    index = resolve_links(index, "root", all_movie_slugs, all_article_slugs)
    root_index.write_text(index, encoding="utf-8")

    # Render search
    search_page = render_search(base_template, search_template, movies, metadata_by_slug)
    search_page = resolve_links(search_page, "public", all_movie_slugs, all_article_slugs)
    root_search.write_text(search_page, encoding="utf-8")

    # Render articles search/index page
    articles_page = render_articles_page(base_template, articles_template, articles)
    articles_page = resolve_links(articles_page, "public", all_movie_slugs, all_article_slugs)
    (output_dir / "articles.html").write_text(articles_page, encoding="utf-8")

    # Render coming soon
    coming_soon = render_coming_soon(base_template, coming_soon_template)
    coming_soon = resolve_links(coming_soon, "public", all_movie_slugs, all_article_slugs)
    (output_dir / "coming-soon.html").write_text(coming_soon, encoding="utf-8")

    # Render greats page
    greats_page = render_greats(base_template, greats_template, great_movies)
    greats_page = resolve_links(greats_page, "public", all_movie_slugs, all_article_slugs)
    (output_dir / "greats.html").write_text(greats_page, encoding="utf-8")

    # Render collections index
    cols_index = render_collections_index(base_template, collections_index_template, collections, metadata_by_slug)
    cols_index = resolve_links(cols_index, "collection", all_movie_slugs, all_article_slugs)
    (collections_dir / "index.html").write_text(cols_index, encoding="utf-8")

    # Render collection details
    for col in collections:
        col_page = render_collection_detail(base_template, collection_detail_template, col, movies_with_metadata)
        col_page = resolve_links(col_page, "collection", all_movie_slugs, all_article_slugs)
        (collections_dir / f"{col.slug}.html").write_text(col_page, encoding="utf-8")


def render_movie(
    base_template: Any,
    movie_template: Any,
    movie: MovieContent,
    metadata: dict[str, Any],
    all_movies: list[tuple[MovieContent, dict[str, Any]]],
) -> str:
    metadata = {**metadata, **_score_metadata(movie)}
    
    director_movies = _get_director_movies(movie, metadata, all_movies)
    director_slugs = {dm["slug"] for dm in director_movies}
    similar_movies = _get_similar_movies(movie, metadata, all_movies, exclude_slugs=director_slugs)
    
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
            "imdb_score": metadata.get("imdb_score") or "",
            "tagline": movie.tagline or metadata.get("tagline", ""),
            "metadata": metadata,
            "similar_movies": similar_movies,
            "director_movies": director_movies,
        }
    )
    
    content = movie_template.render(**movie_data)
    return base_template.render(
        title=f"{movie.title} | The Prolog",
        date=datetime.date.today(),
        content=content,
        css_path="../styles.css",
        home_path="../../index.html",
        search_path="../search.html",
        collections_path="../collections/index.html",
        greats_path="../greats.html",
        coming_soon_path="../coming-soon.html",
        theme_toggle_js_path="../assets/js/theme-toggle.js",
        articles_path="../articles.html",
        favicon_path="../favicon.png",
    )



def render_index(
    base_template: Any,
    index_template: Any,
    movies: list[MovieContent],
    metadata_by_slug: dict[str, dict[str, Any]],
    collections: list[CollectionContent],
    great_movies: list[dict[str, Any]],
) -> str:
    reviewed_count = sum(1 for movie in movies if movie.reviewed)
    
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
    
    # Map dynamic greats relative path for home page
    home_great_movies = []
    for g in great_movies:
        card = next((c for c in movie_cards_data if c["movie"].slug == g["movie"].slug), None)
        if card:
            home_great_movies.append(card)

    content = index_template.render(
        movie_cards=movie_cards_data,
        reviewed_count=reviewed_count,
        total_count=len(movies),
        random_teaser=random_teaser,
        new_reviews=new_reviews,
        great_movies=home_great_movies,
        latest_sidebar=latest_sidebar,
        collections=collections,
    )
    return base_template.render(
        title="The Prolog",
        date=datetime.date.today(),
        content=content,
        css_path="public/styles.css",
        home_path="index.html",
        search_path="public/search.html",
        collections_path="public/collections/index.html",
        greats_path="public/greats.html",
        coming_soon_path="public/coming-soon.html",
        theme_toggle_js_path="public/assets/js/theme-toggle.js",
        articles_path="public/articles.html",
        favicon_path="favicon.png",
    )


def render_coming_soon(
    base_template: Any,
    coming_soon_template: Any,
) -> str:
    content = coming_soon_template.render(home_path="../index.html")
    return base_template.render(
        title="Coming Soon | The Prolog",
        date=datetime.date.today(),
        content=content,
        css_path="styles.css",
        home_path="../index.html",
        search_path="search.html",
        collections_path="collections/index.html",
        greats_path="greats.html",
        coming_soon_path="coming-soon.html",
        theme_toggle_js_path="assets/js/theme-toggle.js",
        articles_path="articles.html",
        favicon_path="favicon.png",
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
        date=datetime.date.today(),
        content=content,
        css_path="styles.css",
        home_path="../index.html",
        search_path="search.html",
        collections_path="collections/index.html",
        greats_path="greats.html",
        coming_soon_path="coming-soon.html",
        theme_toggle_js_path="assets/js/theme-toggle.js",
        articles_path="articles.html",
        favicon_path="favicon.png",
    )


def render_articles_page(
    base_template: Any,
    articles_template: Any,
    articles: list[ArticleContent],
) -> str:
    content = articles_template.render(
        articles=articles,
        articles_js_path="assets/js/articles-controller.js"
    )
    return base_template.render(
        title="Articles & Essays | The Prolog",
        date=datetime.date.today(),
        content=content,
        css_path="styles.css",
        home_path="../index.html",
        search_path="search.html",
        collections_path="collections/index.html",
        greats_path="greats.html",
        coming_soon_path="coming-soon.html",
        theme_toggle_js_path="assets/js/theme-toggle.js",
        articles_path="articles.html",
        favicon_path="favicon.png",
    )


def render_article(
    base_template: Any,
    article_template: Any,
    article: ArticleContent,
) -> str:
    content = article_template.render(
        title=article.title,
        author=article.author,
        date=article.date,
        body=article.body,
    )
    return base_template.render(
        title=f"{article.title} | The Prolog",
        date=datetime.date.today(),
        content=content,
        css_path="../styles.css",
        home_path="../../index.html",
        search_path="../search.html",
        collections_path="../collections/index.html",
        greats_path="../greats.html",
        coming_soon_path="../coming-soon.html",
        theme_toggle_js_path="../assets/js/theme-toggle.js",
        articles_path="../articles.html",
        favicon_path="../favicon.png",
    )


def render_greats(
    base_template: Any,
    greats_template: Any,
    great_movies: list[dict[str, Any]],
) -> str:
    # Adjust poster URLs for greats page to be relative to public/ directory
    adjusted_great_movies = []
    for g in great_movies:
        card = dict(g)
        poster = card.get("poster_url", "")
        if poster.startswith("public/"):
            card["poster_url"] = poster.replace("public/", "", 1)
        adjusted_great_movies.append(card)

    content = greats_template.render(
        great_movies=adjusted_great_movies,
    )
    return base_template.render(
        title="The Greats | The Prolog",
        date=datetime.date.today(),
        content=content,
        css_path="styles.css",
        home_path="../index.html",
        search_path="search.html",
        collections_path="collections/index.html",
        greats_path="greats.html",
        coming_soon_path="coming-soon.html",
        theme_toggle_js_path="assets/js/theme-toggle.js",
        articles_path="articles.html",
        favicon_path="favicon.png",
    )


def _assign_collection_posters(
    collections: list[CollectionContent],
    metadata_by_slug: dict[str, dict[str, Any]]
) -> dict[str, str | None]:
    """
    Randomly assigns a unique movie poster (by movie slug) to each collection.
    If a unique assignment is mathematically impossible, falls back to choosing
    a random movie from each collection's list.
    """
    assigned = {}
    used_movies = set()

    # Get the list of movies for each collection
    col_movies = {}
    collections_to_assign = []
    for col in collections:
        if col.movies:
            col_movies[col.slug] = list(col.movies)
            collections_to_assign.append(col)
        else:
            assigned[col.slug] = None

    def backtrack(col_index, sorted_cols):
        if col_index == len(sorted_cols):
            return True
        col_slug = sorted_cols[col_index]
        options = list(col_movies[col_slug])
        random.shuffle(options)
        
        for movie_slug in options:
            if movie_slug not in used_movies:
                used_movies.add(movie_slug)
                assigned[col_slug] = movie_slug
                if backtrack(col_index + 1, sorted_cols):
                    return True
                used_movies.remove(movie_slug)
                del assigned[col_slug]
        return False

    # Sort collections by number of movie options (most constrained first)
    sorted_cols = sorted(collections_to_assign, key=lambda c: len(col_movies[c.slug]))
    sorted_col_slugs = [c.slug for c in sorted_cols]

    success = backtrack(0, sorted_col_slugs)
    
    if not success:
        # Fallback: choose random movie for each collection, allowing duplicates
        for col in collections:
            options = col.movies
            if options:
                assigned[col.slug] = random.choice(options)
            else:
                assigned[col.slug] = None

    return assigned


def render_collections_index(
    base_template: Any,
    collections_template: Any,
    collections: list[CollectionContent],
    metadata_by_slug: dict[str, dict[str, Any]],
) -> str:
    assigned_posters = _assign_collection_posters(collections, metadata_by_slug)
    
    collections_data = []
    for col in collections:
        assigned_movie_slug = assigned_posters.get(col.slug)
        poster_url = None
        if assigned_movie_slug:
            movie_metadata = metadata_by_slug.get(assigned_movie_slug, {})
            poster_url = movie_metadata.get("poster_url") or "assets/placeholders/poster-placeholder.svg"
            if poster_url.startswith("public/"):
                poster_url = poster_url.replace("public/", "../", 1)
            elif not poster_url.startswith("http"):
                poster_url = "../" + poster_url
        else:
            poster_url = "../assets/placeholders/poster-placeholder.svg"

        collections_data.append({
            "title": col.title,
            "slug": col.slug,
            "teaser": col.teaser,
            "movies": col.movies,
            "poster_url": poster_url,
        })

    content = collections_template.render(
        collections=collections_data,
    )
    return base_template.render(
        title="Collections | The Prolog",
        date=datetime.date.today(),
        content=content,
        css_path="../styles.css",
        home_path="../../index.html",
        search_path="../search.html",
        collections_path="index.html",
        greats_path="../greats.html",
        coming_soon_path="../coming-soon.html",
        theme_toggle_js_path="../assets/js/theme-toggle.js",
        articles_path="../articles.html",
        favicon_path="../favicon.png",
    )


def render_collection_detail(
    base_template: Any,
    collection_detail_template: Any,
    collection: CollectionContent,
    all_movies: list[tuple[MovieContent, dict[str, Any]]],
) -> str:
    movie_cards_data = []
    for movie_slug in collection.movies:
        match = next((item for item in all_movies if item[0].slug == movie_slug), None)
        if match:
            movie, metadata = match
            poster_url = metadata.get("poster_url") or "assets/placeholders/poster-placeholder.svg"
            if poster_url.startswith("public/"):
                poster_url = poster_url.replace("public/", "../", 1)
            elif not poster_url.startswith("http"):
                poster_url = "../" + poster_url
                
            movie_cards_data.append({
                "movie": movie,
                "metadata": metadata,
                "poster_url": poster_url,
                "director": metadata.get("director") or "Director unavailable",
                "tagline": movie.tagline or metadata.get("tagline", ""),
            })

    content = collection_detail_template.render(
        collection=collection,
        movie_cards=movie_cards_data,
    )
    return base_template.render(
        title=f"{collection.title} | The Prolog",
        date=datetime.date.today(),
        content=content,
        css_path="../styles.css",
        home_path="../../index.html",
        search_path="../search.html",
        collections_path="index.html",
        greats_path="../greats.html",
        coming_soon_path="../coming-soon.html",
        theme_toggle_js_path="../assets/js/theme-toggle.js",
        articles_path="../articles.html",
        favicon_path="../favicon.png",
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
    exclude_slugs: set[str] | None = None,
) -> list[dict[str, Any]]:
    scored_movies = []
    current_genres = set(current_metadata.get("genres", []))
    current_director = current_metadata.get("director", "")
    current_year = current_movie.year or current_metadata.get("release_date", "")[:4]

    for other_movie, other_metadata in all_movies:
        if other_movie.slug == current_movie.slug:
            continue
        if exclude_slugs and other_movie.slug in exclude_slugs:
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


def _get_director_movies(
    current_movie: MovieContent,
    current_metadata: dict[str, Any],
    all_movies: list[tuple[MovieContent, dict[str, Any]]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    current_director = current_metadata.get("director", "")
    if not current_director or current_director == "Director unavailable":
        return []
    
    current_directors = {d.strip().lower() for d in current_director.split(",") if d.strip()}
    if not current_directors:
        return []
        
    matching_movies = []
    for other_movie, other_metadata in all_movies:
        if other_movie.slug == current_movie.slug:
            continue
            
        other_director = other_metadata.get("director", "")
        if not other_director or other_director == "Director unavailable":
            continue
            
        other_directors = {d.strip().lower() for d in other_director.split(",") if d.strip()}
        
        if current_directors & other_directors:
            score = 0.0
            if other_movie.reviewed:
                score += 1000.0
                
            w_score = get_weighted_score(other_movie, other_metadata)
            if w_score is not None:
                score += w_score
            else:
                imdb_val = other_metadata.get("imdb_score") or other_movie.scores.get("IMDb score")
                if imdb_val:
                    try:
                        clean_val = str(imdb_val).split("/")[0].strip()
                        score += float(clean_val)
                    except ValueError:
                        pass
                else:
                    try:
                        score += float(other_metadata.get("vote_average") or 0.0)
                    except ValueError:
                        pass
                        
            matching_movies.append((score, other_movie, other_metadata))
            
    def sort_key(item):
        score, movie, meta = item
        try:
            year_val = int(movie.year or meta.get("release_date", "")[:4])
        except ValueError:
            year_val = 0
        return -score, -year_val, movie.title.lower()
        
    matching_movies.sort(key=sort_key)
    
    director_movies = []
    for score, m, meta in matching_movies[:limit]:
        director_movies.append({
            "title": m.title,
            "slug": m.slug,
            "poster_url": meta.get("poster_url") or "../assets/placeholders/poster-placeholder.svg",
            "year": m.year or meta.get("release_date", "")[:4],
        })
        
    return director_movies
