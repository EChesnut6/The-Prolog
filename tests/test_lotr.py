import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tmdb import fetch_movie_metadata

def test():
    title = "The Lord of the Rings The Return of the King"
    year = "2003"
    print(f"Testing lookup for: {title} ({year})")
    try:
        metadata = fetch_movie_metadata(title, year)
        print(f"Metadata: {metadata}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test()
