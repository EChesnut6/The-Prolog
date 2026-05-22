# The-Prolog
Appreciate the artistic intent of a film without spoilers.

## Architecture

The Prolog is a local Python static site generator for spoiler-light pre-flight checklists, reviews, historical context, and visual references.

- `content/movies/*.md` stores one movie per Markdown file. Each file has simple `---` front matter plus `Primer`, `Technical Footnotes`, `Review`, and `Gallery` sections.
- `src/content.py` parses movie files, derives review status, converts Markdown to HTML, and sorts reviewed movies ahead of draft templates.
- `src/tmdb.py` fetches TMDB metadata and optional OMDb IMDb ratings when API keys are available.
- `src/metadata_cache.py` reads and writes `.tmdb-cache.json`; cache entries are refreshed when the source Markdown hash, TMDB title, or year changes.
- `src/render.py` renders Jinja templates from `templates/` into static pages.
- `src/build.py` orchestrates loading content, metadata enrichment, optional asset copying, and rendering.

The build writes static HTML to:

- Root `index.html` for the GitHub Pages homepage.
- Root `search.html` for movie search.
- `public/reviews/*.html` for individual movie pages.
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
- `--prompt-specs` prompts for optional technical spec fields.
- `--force` overwrites an existing draft with the same slug.
- `--reviewed` makes the movie visible on the default homepage view. Draft templates use `reviewed: false` and remain searchable.

Or create a new Markdown file in `content/movies/` using an existing review as a guide. The generator expects front matter plus these sections:

- `Primer`
- `Technical Footnotes`
- `Review`
- `Gallery`

Optional structured technical spec fields can be added to front matter:

```text
reviewed: false
enjoyment_rating: 8
filmmaking_rating: 9
letterboxd_score: 4.5/5
imdb_score: 8.7/10
aspect_ratio: 2.39:1
visual_texture: High-contrast digital photography
sound_world: Practical engine noise and sparse score
format: Digital
camera_lens: Long-lens urban scale
technical_notes: Any concise note worth surfacing as metadata
```

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
