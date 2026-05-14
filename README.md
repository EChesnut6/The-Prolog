# The-Prolog
Appreciate the artistic intent of a film without spoilers.

## Architecture

The Prolog is a local Python static site generator for spoiler-light pre-flight checklists, reviews, historical context, and visual references. It reads movie notes from `content/movies/`, optionally enriches them with TMDB metadata, renders HTML templates from `templates/`, writes review pages/assets to `public/`, and writes the GitHub Pages entrypoint to root `index.html`.

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

Open `index.html` in a browser to view the generated site. The root index is intentional for GitHub Pages.

## Add A Movie

Create a draft with the CLI:

```sh
python3 src/new_review.py --prompt-specs
```

Or create a new Markdown file in `content/movies/` using an existing review as a guide. The generator expects front matter plus these sections:

- `Primer`
- `Technical Footnotes`
- `Review`
- `Gallery`

Optional structured technical spec fields can be added to front matter:

```text
reviewed: false
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
