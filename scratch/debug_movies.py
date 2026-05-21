from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.content import load_movies

CONTENT_DIR = ROOT / "content" / "movies"

def debug():
    movies = load_movies(CONTENT_DIR)
    print(f"Total movies loaded: {len(movies)}")
    lotr = [m for m in movies if "Lord of the Rings" in m.title]
    print(f"LOTR movies: {[m.title for m in lotr]}")
    for m in lotr:
        print(f"Slug: {m.slug}, TMDB Title: {m.tmdb_title}")

if __name__ == "__main__":
    debug()
