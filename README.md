# The-Prolog
Learn the context of your next watch. Go in knowing a touch more than nothing and a little less than a trailer.

## Architecture

The Prolog is a local Python static site generator. It reads movie notes from `content/movies/`, optionally enriches them with TMDB metadata, renders HTML templates from `templates/`, and writes the static website to `public/`.

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
```

The site still builds without a key. It will use local placeholder metadata and poster art.

## Build

```sh
python3 src/build.py
```

Builds use `.tmdb-cache.json` to avoid repeated TMDB API calls for unchanged reviews. To force fresh metadata:

```sh
python3 src/build.py --refresh-metadata
```

Open `public/index.html` in a browser to view the generated site.

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
aspect_ratio: 2.39:1
visual_texture: High-contrast digital photography
sound_world: Practical engine noise and sparse score
format: Digital
camera_lens: Long-lens urban scale
technical_notes: Any concise note worth surfacing as metadata
```
