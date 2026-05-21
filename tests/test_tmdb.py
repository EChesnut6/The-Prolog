import os
import sys

# Add the project root to sys.path to allow importing from 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tmdb import fetch_movie_metadata, _search_movie, _movie_details

def get_tmdb_datapoints(title: str, year: str = "") -> list[str]:
    """Returns a list of all keys available in the raw TMDB response."""
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("TMDB_API_KEY not found in environment.")
        return []
    
    movie = _search_movie(api_key, title, year)
    if not movie:
        print(f"No movie found for {title}")
        return []
        
    details = _movie_details(api_key, movie["id"])
    
    # Combine keys from search and details
    all_keys = set(movie.keys()) | set(details.keys())
    return sorted(list(all_keys))

def test_fetch_movie():
    title = "Inception"
    year = "2010"
    print(f"--- Testing TMDB API Metadata Fetch for: {title} ({year}) ---")
    
    metadata = fetch_movie_metadata(title, year)
    
    if metadata:
        print("Success! Filtered metadata fetched:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
    else:
        print("Failed to fetch metadata. Check your API keys and internet connection.")

def test_raw_datapoints():
    title = "Inception"
    year = "2010"
    print(f"\n--- Listing all available raw TMDB datapoints for: {title} ({year}) ---")
    
    datapoints = get_tmdb_datapoints(title, year)
    if datapoints:
        print(f"Found {len(datapoints)} raw datapoints:")
        for point in datapoints:
            print(f"  - {point}")
    else:
        print("Could not retrieve raw datapoints.")

if __name__ == "__main__":
    test_fetch_movie()
    test_raw_datapoints()
