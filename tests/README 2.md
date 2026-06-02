# Tests

This folder contains scripts to test the project's functionality.

## TMDB API Test

The `test_tmdb.py` script includes tests for:
- `fetch_movie_metadata`: Verifies the filtered metadata used by the site.
- `get_tmdb_datapoints`: Lists all raw keys available from the TMDB API (useful for discovering new data to use).

### How to run

From the project root, run:

```bash
.venv/bin/python3 tests/test_tmdb.py
```

Make sure you have a `.env` file in the project root with the following keys:
- `TMDB_API_KEY`
- `OMDB_API_KEY` (optional, for IMDb scores)
