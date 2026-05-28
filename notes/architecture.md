# Architecture

The Prolog is a Python static site generator for film pages. It stores reviews and pre-view notes as Markdown, enriches them with movie metadata when API keys are available, and renders static HTML for GitHub Pages-style hosting.

## System Overview

```text
content/movies/*.md
        |
        v
src/content.py
  parse front matter, sections, ratings, review status
        |
        v
src/build.py
  load content, load metadata cache, fetch missing metadata
        |
        v
src/render.py + templates/*.html
  render Jinja templates into static HTML
        |
        v
index.html
public/search.html
public/reviews/*.html
public/coming-soon.html
public/styles.css
```

The generated site is static. Runtime interactivity is limited to browser-side JavaScript in the rendered templates, mainly theme switching and search filtering.

## Project Layout

```text
.
├── content/
│   └── movies/                 # Source Markdown files, one movie per file
├── src/
│   ├── build.py                # Build orchestration entry point
│   ├── content.py              # Markdown/front matter parsing and MovieContent model
│   ├── metadata_cache.py       # TMDB/OMDb metadata cache read/write/freshness logic
│   ├── new_review.py           # CLI for creating new movie Markdown drafts
│   ├── render.py               # Jinja rendering for all site pages
│   └── tmdb.py                 # TMDB and optional OMDb API integration
├── templates/
│   ├── base.html               # Shared page shell, nav, footer, theme toggle
│   ├── index.html              # Homepage sections
│   ├── movie.html              # Individual movie page body
│   ├── search.html             # Search page body and browser-side search logic
│   └── coming-soon.html        # Placeholder page for unfinished sections
├── public/
│   ├── reviews/                # Generated movie review pages
│   ├── search.html             # Generated browser-side search page
│   ├── styles.css              # Static stylesheet used by generated pages
│   └── coming-soon.html        # Generated placeholder page
├── scripts/
│   └── create_letterboxd_top_templates.py
├── tests/                      # Script-style checks and debugging helpers
├── index.html                  # Generated root homepage (kept at root for hosting root entry point)
├── requirements.txt            # Python dependencies
└── README.md                   # Setup, build, and usage notes
```

## Source Content Model

Each movie begins as a Markdown file in `content/movies/`. The file contains simple front matter followed by named Markdown sections.

Required or commonly used front matter:

```yaml
---
title: Vanilla Sky
slug: vanilla-sky
tmdb_title: Vanilla Sky
year: 2001
enjoyment_rating: 8
filmmaking_rating: 9
reviewed: true
---
```

Supported optional fields include:

- `tagline`
- `letterboxd_rank`
- `letterboxd_source`
- `letterboxd_score`
- `imdb_score`

The parser in `src/content.py` converts each file into a `MovieContent` dataclass. It calculates a source hash for cache freshness and uses file modification time for sorting.

Current rendered sections:

- `Primer`: spoiler-light context shown before the review (rendered under "The Primer").
- `Review`: full critique hidden behind a spoiler reveal.

Note: The naming mismatch between `Primer` (used in templates, the CLI generator, and readme references) and `Pre-View` (previously used in the parser) has been resolved. The parser in [content.py](file:///Users/elichesnut/documents/github/the-prolog/src/content.py) reads the `Primer` section from the markdown files.

## Build Flow

The main build entry point is:

```sh
python3 src/build.py
```

`src/build.py` performs these steps:

1. Load all Markdown files from `content/movies/`.
2. Parse each file with `src/content.py`.
3. Load metadata from `.tmdb-cache.json`.
4. For each movie, reuse cached metadata if the source hash, TMDB title, and year still match.
5. Fetch fresh metadata through `src/tmdb.py` when cache data is missing or stale.
6. Save the metadata cache if new entries were fetched.
7. Copy root `assets/` into `public/assets/` if an `assets/` directory exists.
8. Render the site through `src/render.py`.

Useful build options:

```sh
python3 src/build.py --refresh-metadata
python3 src/build.py --metadata-cache path/to/cache.json
```

## Metadata Flow

`src/tmdb.py` fetches external metadata when `TMDB_API_KEY` is present in the environment. It searches TMDB by `tmdb_title` and optional `year`, then requests details with credits and external IDs.

Fetched TMDB fields include:

- TMDB ID
- IMDb ID
- poster URL
- backdrop URL
- release date
- director
- runtime
- genres
- TMDB vote average
- tagline

If `OMDB_API_KEY` is present and TMDB provides an IMDb ID, the code also fetches an IMDb score from OMDb.

If keys are missing, `requests` is unavailable, or a lookup fails, the build continues with cached data or empty metadata. Templates fall back to placeholder poster paths and unavailable text.

## Rendering

`src/render.py` owns all page rendering. It creates a Jinja environment from `templates/`, renders page-specific content, then wraps that content in `templates/base.html`.

Generated pages:

- `index.html`: homepage at the repository root.
- `public/search.html`: search page under the public directory.
- `public/reviews/{slug}.html`: one movie page per Markdown file.
- `public/coming-soon.html`: placeholder page for unfinished nav sections.

The root homepage (`index.html`) links to styles at `public/styles.css`, reviews at `public/reviews/{slug}.html`, the search page at `public/search.html`, and coming-soon at `public/coming-soon.html`.
Pages within the `public/` directory (like `public/search.html` and `public/coming-soon.html`) access styles locally via `styles.css` and use relative routes like `reviews/{slug}.html` or `../index.html`.
Individual review pages under `public/reviews/` use relative paths such as `../styles.css`, `../../index.html`, and `../search.html`.

## Homepage Behavior

The homepage is built from reviewed movies only for its main visible sections.

`render_index()` prepares:

- `random_teaser`: one random reviewed movie for the hero.
- `new_reviews`: the first four reviewed movies after content sorting.
- `latest_sidebar`: the first ten reviewed movies.
- `great_movies`: reviewed movies with `filmmaking_rating >= 9`.

Content sorting happens in `load_movies()`:

1. Reviewed movies first.
2. Newer file modification time first.
3. Title as a final alphabetical tie-breaker.

## Search Behavior

The search page receives every movie, including drafts/templates. The page embeds a JavaScript `movies` array at build time and filters in the browser.

Search currently matches:

- Title first.
- Director second.

The page also includes pagination with a default page size of 40 results.

New movie files can be created through:

```sh
python3 src/new_review.py
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

Drafts default to `reviewed: false`, which keeps them out of the homepage sections while still allowing them to appear in search.

## Dependencies

Runtime dependencies are listed in `requirements.txt`:

- `requests`: HTTP calls for TMDB and OMDb.
- `python-dotenv`: loading `.env` API keys.
- `Jinja2`: HTML template rendering.
- `markdown`: Markdown-to-HTML conversion.

## Tests And Debugging

The `tests/` directory contains script-style checks rather than a formal test suite.

Current scripts:

- `tests/test_tmdb.py`: checks TMDB metadata fetching and explores available TMDB fields.
- `tests/test_lotr.py`: targeted TMDB lookup/debug script.
- `tests/debug_movies.py`: local content/build debugging helper.

TMDB-related scripts require `TMDB_API_KEY`. OMDb remains optional.

## Current Architecture Notes

- The source of truth is `content/movies/*.md`; generated HTML in `index.html`, `public/search.html`, and `public/reviews/` should be treated as build output.
- The metadata cache is keyed by movie slug and invalidated by source hash, TMDB title, and year.
- There is no server-side runtime after build; deployment can serve static files directly.
- Navigation links for `Collections` and `Greats` currently point to the generated coming-soon page.
- `public/styles.css` is maintained as a static stylesheet, not generated from a CSS build pipeline.
- The parser in [content.py](file:///Users/elichesnut/documents/github/the-prolog/src/content.py) reads the `Primer` section, resolving the previous naming mismatch with `Pre-View`.
