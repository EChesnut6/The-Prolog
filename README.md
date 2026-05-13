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

Open `public/index.html` in a browser to view the generated site.

## Add A Movie

Create a new Markdown file in `content/movies/` using the sample file as a guide. The generator expects front matter plus these sections:

- `Primer`
- `Technical Footnotes`
- `Review`
- `Gallery`
