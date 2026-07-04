# The-Prolog
Appreciate the artistic intent of a film without spoilers.

## Architecture

The Prolog is a local Python static site generator for spoiler-light pre-flight checklists, reviews, historical context, and visual references.

- `content/movies/*.md` stores movie reviews. Each file has simple `---` front matter plus `Primer` and `Review` sections.
- `content/collections/*.md` stores movie collections.
- `content/articles/*.md` stores journal articles and essays.
- `src/content.py` parses movie reviews, collections, and articles, converting Markdown to HTML with auto-resolving wiki-links.
- `src/tmdb.py` fetches TMDB metadata and optional OMDb IMDb ratings when API keys are available.
- `src/metadata_cache.py` reads and writes `.tmdb-cache.json`; cache entries are refreshed when the source Markdown hash, TMDB title, or year changes.
- `src/render.py` renders Jinja templates from `templates/` into static pages.
- `src/build.py` orchestrates loading content, metadata enrichment, optional asset copying, and rendering.

The build writes static HTML to:

- Root `index.html` for the GitHub Pages homepage.
- Root `search.html` for movie search.
- `public/reviews/*.html` for individual movie pages.
- `public/collections/*.html` for thematic movie collections.
- `public/articles.html` for the articles search & listing directory page.
- `public/articles/*.html` for individual journal articles & essays.
- `public/coming-soon.html`.
- `public/assets/` when a root `assets/` directory exists; otherwise templates fall back to placeholder asset paths.

`public/styles.css` is the static stylesheet referenced by the generated pages.

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your TMDB API key to `.env`:

```text
TMDB_API_KEY=your_api_key_here
OMDB_API_KEY=your_omdb_key_here
```

The OMDb key is optional and only used to fetch IMDb ratings when a TMDB match has an IMDb ID. The site still builds without keys. It will use cached metadata or local placeholder metadata and poster art.

## Build

```sh
python3 src/build.py
```

Builds use `.tmdb-cache.json` to avoid repeated TMDB API calls for unchanged reviews. To force fresh metadata:

```sh
python3 src/build.py --refresh-metadata
```

To use a different cache file:

```sh
python3 src/build.py --metadata-cache path/to/cache.json
```

Open `index.html` in a browser to view the generated site. The root `index.html` and `search.html` are intentional for GitHub Pages; review pages are written under `public/reviews/`.

## Manage Content (CLI Workflow Manager)

To manage your writing process, list drafts, check status, edit metadata, preview content, and open reviews/articles in the **Texodus** editor, launch the interactive content manager:

```sh
python3 src/manage_reviews.py
```

You can also run commands non-interactively for quick updates by grouping them into `review`, `collection`, or `article` subparsers:

### Reviews
- **List reviews by status:** `python3 src/manage_reviews.py review list --status draft`
- **Check a review's details:** `python3 src/manage_reviews.py review status perfect-blue`
- **Open a review in Texodus:** `python3 src/manage_reviews.py review open perfect-blue`
- **Quickly print review content:** `python3 src/manage_reviews.py review preview perfect-blue`
- **Update ratings or toggle published status (and optionally auto-rebuild):**
  ```sh
  python3 src/manage_reviews.py review update perfect-blue --enjoyment 9 --filmmaking 10 --reviewed true --rebuild
  ```
- **Create a new review:**
  ```sh
  python3 src/manage_reviews.py review create --title "The Matrix" --year 1999 --rebuild
  ```

### Collections
- **List all collections:** `python3 src/manage_reviews.py collection list`
- **Check collection details and movie statuses:** `python3 src/manage_reviews.py collection status classics`
- **Create a collection:** `python3 src/manage_reviews.py collection create --title "Noir Classics" --teaser "Drenched in rain." --movies "double-indemnity,chinatown" --rebuild`

### Articles
- **List all articles:** `python3 src/manage_reviews.py article list`
- **Check article metadata status:** `python3 src/manage_reviews.py article status the-evolution-of-comedy`
- **Open an article in Texodus:** `python3 src/manage_reviews.py article open the-evolution-of-comedy`
- **Update article details:** `python3 src/manage_reviews.py article update the-evolution-of-comedy --author "Eli Chesnut" --rebuild`
- **Create a new article:** `python3 src/manage_reviews.py article create --title "Visual Metaphors" --teaser "On modern framing." --rebuild`

## Add A Movie

Create a draft with the CLI:

```sh
python3 src/new_review.py --prompt-specs
```

The CLI can also run non-interactively:

```sh
python3 src/new_review.py \
  --title "Movie Title" \
  --year 2026 \
  --enjoyment-rating 8 \
  --filmmaking-rating 9 \
  --reviewed
```

Useful options:

- `--slug` sets the Markdown filename and generated review URL.
- `--tmdb-title` overrides the title used for TMDB search.
- `--force` overwrites an existing draft with the same slug.
- `--reviewed` makes the movie visible on the default homepage view. Draft templates use `reviewed: false` and remain searchable.

Or create a new Markdown file in `content/movies/` using an existing review as a guide. The generator expects front matter plus these sections:

- `Primer`
- `Review`

Optional scoring and review override fields can be added to front matter:

```text
reviewed: false
enjoyment_rating: 8
filmmaking_rating: 9
letterboxd_score: 4.5/5
imdb_score: 8.7/10
```

## Add An Article

Create an article draft with the CLI:

```sh
python3 src/manage_reviews.py article create --title "Article Title" --teaser "Article Teaser" --rebuild
```

Or create a new Markdown file in `content/articles/` (e.g. `content/articles/my-essay.md`). The generator expects front matter with these fields:

```yaml
---
title: My Essay Title
slug: my-essay-slug
teaser: A summary of this essay.
author: Author Name
date: YYYY-MM-DD
---
```

You can use wiki-links inside the article body (e.g. `[[the-lighthouse]]` or `[[the-evolution-of-comedy]]`) to auto-resolve to links within the site.

## Letterboxd Templates

Generate missing templates from the saved Letterboxd list:

```sh
python3 scripts/create_letterboxd_top_templates.py
```

The generator skips files that already exist and marks new templates as `reviewed: false`, so they stay off the default homepage view until someone searches for them.

## Tests And Debugging

The `tests/` folder contains small script-style checks rather than a formal test runner:

```sh
.venv/bin/python3 tests/test_tmdb.py
.venv/bin/python3 tests/test_lotr.py
.venv/bin/python3 tests/debug_movies.py
```

`tests/test_tmdb.py` and `tests/test_lotr.py` require `TMDB_API_KEY` for live metadata calls. `OMDB_API_KEY` remains optional and only affects IMDb score enrichment.
