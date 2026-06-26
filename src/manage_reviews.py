from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Fix python path to allow importing from src
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.content import load_movies, load_movie, MovieContent, load_collections, load_collection, CollectionContent
from src.utils import slugify, render_review_template

CONTENT_DIR = ROOT / "content" / "movies"
COLLECTIONS_DIR = ROOT / "content" / "collections"

# Terminal Color Codes
def color(text: str, color_code: str) -> str:
    if sys.stdout.isatty():
        return f"\033[{color_code}m{text}\033[0m"
    return text

BOLD = "1"
DIM = "2"
RED = "31"
GREEN = "32"
YELLOW = "33"
BLUE = "34"
MAGENTA = "35"
CYAN = "36"

def print_title(title: str) -> None:
    print("\n" + color("=" * 60, BLUE))
    print(color(title.center(60), BOLD + ";" + BLUE))
    print(color("=" * 60, BLUE))

# --- Review Helpers ---

def get_status(movie: MovieContent, path: Path) -> str:
    if movie.reviewed:
        return "Reviewed"
    
    if not path.exists():
        return "Unknown"
        
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return "Unknown"
        
    template_markers = (
        "Draft review template",
        "Draft pre-flight checklist template",
        "Add spoiler-light context",
        "Write the full critique here.",
    )
    if any(marker in content for marker in template_markers):
        return "Draft"
    else:
        return "In Progress"

def load_all_reviews() -> list[dict]:
    movies = load_movies(CONTENT_DIR)
    reviews = []
    for movie in movies:
        path = CONTENT_DIR / f"{movie.slug}.md"
        status = get_status(movie, path)
        reviews.append({
            "movie": movie,
            "status": status,
            "path": path,
            "last_modified": path.stat().st_mtime if path.exists() else 0.0
        })
    # Sort: In Progress first, then Draft, then Reviewed, sub-sorting by last modified desc
    status_order = {"In Progress": 0, "Draft": 1, "Reviewed": 2}
    reviews.sort(key=lambda r: (status_order.get(r["status"], 3), -r["last_modified"]))
    return reviews

def update_review_metadata(path: Path, updates: dict[str, Any]) -> bool:
    if not path.exists():
        print(color(f"Error: File {path} does not exist.", RED))
        return False
    
    try:
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---\n"):
            print(color("Error: File does not start with YAML front matter (---).", RED))
            return False
            
        parts = raw.split("---", 2)
        if len(parts) < 3:
            print(color("Error: Incomplete front matter delimiter.", RED))
            return False
            
        front_matter_str = parts[1]
        body = parts[2]
        
        lines = front_matter_str.splitlines()
        new_lines = []
        updated_keys = set()
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue
            if stripped.startswith("-"):
                new_lines.append(line)
                continue
                
            key, separator, value = line.partition(":")
            if not separator:
                new_lines.append(line)
                continue
                
            key_str = key.strip()
            if key_str in updates:
                val = updates[key_str]
                if isinstance(val, bool):
                    val_str = "true" if val else "false"
                else:
                    val_str = str(val)
                new_lines.append(f"{key_str}: {val_str}")
                updated_keys.add(key_str)
            else:
                new_lines.append(line)
                
        for key, val in updates.items():
            if key not in updated_keys:
                if isinstance(val, bool):
                    val_str = "true" if val else "false"
                else:
                    val_str = str(val)
                new_lines.append(f"{key}: {val_str}")
                
        new_front_matter = "\n".join(new_lines)
        path.write_text(f"---{new_front_matter}\n---{body}", encoding="utf-8")
        return True
    except Exception as e:
        print(color(f"Error updating file metadata: {e}", RED))
        return False

# --- Collection Helpers ---

def load_all_collections() -> list[dict]:
    cols = load_collections(COLLECTIONS_DIR)
    collections = []
    for col in cols:
        path = COLLECTIONS_DIR / f"{col.slug}.md"
        collections.append({
            "collection": col,
            "path": path,
            "last_modified": path.stat().st_mtime if path.exists() else 0.0
        })
    collections.sort(key=lambda c: c["collection"].title.lower())
    return collections

def update_collection_metadata_file(path: Path, updates: dict[str, Any]) -> bool:
    if not path.exists():
        print(color(f"Error: File {path} does not exist.", RED))
        return False
    try:
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---\n"):
            print(color("Error: File does not start with YAML front matter (---).", RED))
            return False
            
        parts = raw.split("---", 2)
        if len(parts) < 3:
            print(color("Error: Incomplete front matter delimiter.", RED))
            return False
            
        front_matter_str = parts[1]
        body = parts[2]
        
        # Parse existing front matter
        metadata: dict[str, Any] = {}
        current_key = None
        for line in front_matter_str.splitlines():
            if not line.strip():
                continue
            if line.strip().startswith("-") and current_key:
                val = line.strip().lstrip("-").strip()
                if not isinstance(metadata[current_key], list):
                    metadata[current_key] = []
                metadata[current_key].append(val)
                continue

            key, separator, value = line.partition(":")
            if not separator:
                continue
            
            key_str = key.strip()
            val_str = value.strip()
            
            if not val_str:
                metadata[key_str] = []
                current_key = key_str
            else:
                metadata[key_str] = val_str
                current_key = key_str
                
        # Apply updates
        for k, v in updates.items():
            metadata[k] = v
            
        # Serialize back to front matter
        new_front_matter = []
        for k, v in metadata.items():
            if isinstance(v, list):
                new_front_matter.append(f"{k}:")
                for item in v:
                    new_front_matter.append(f"  - {item}")
            else:
                new_front_matter.append(f"{k}: {v}")
                
        new_front_matter_str = "\n".join(new_front_matter)
        path.write_text(f"---\n{new_front_matter_str}\n---{body}", encoding="utf-8")
        return True
    except Exception as e:
        print(color(f"Error updating collection metadata: {e}", RED))
        return False

# --- General System Helpers ---

def open_in_texodus(path: Path) -> bool:
    # First attempt: open -a Texodus
    try:
        result = subprocess.run(["open", "-a", "Texodus", str(path)], capture_output=True, text=True)
        if result.returncode == 0:
            print(color("Opened file in Texodus.", GREEN))
            return True
    except Exception:
        pass

    # Fallback 1: EDITOR environment variable
    editor = os.environ.get("EDITOR")
    if editor:
        print(color(f"Texodus app not found or failed to start. Falling back to $EDITOR ({editor})...", YELLOW))
        try:
            subprocess.run([editor, str(path)])
            return True
        except Exception as e:
            print(color(f"Failed to open with $EDITOR '{editor}': {e}", RED))

    # Fallback 2: Default macOS open (system default markdown editor)
    print(color("Falling back to system default Markdown editor...", YELLOW))
    try:
        result = subprocess.run(["open", str(path)], capture_output=True, text=True)
        if result.returncode == 0:
            print(color("Opened file in system default editor.", GREEN))
            return True
        else:
            print(color(f"Failed to open: {result.stderr.strip()}", RED))
            return False
    except Exception as e:
        print(color(f"Failed to open file: {e}", RED))
        return False

def rebuild_site() -> None:
    print(color("\nRebuilding the static site...", YELLOW))
    try:
        result = subprocess.run([sys.executable, str(ROOT / "src" / "build.py")], capture_output=True, text=True)
        if result.returncode == 0:
            print(color("Site successfully rebuilt!", GREEN))
            last_line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
            if last_line:
                print(color(f"  {last_line}", DIM))
        else:
            print(color("Failed to rebuild site:", RED))
            print(result.stderr)
    except Exception as e:
        print(color(f"Error rebuilding site: {e}", RED))

# --- Review Flows & Menus ---

def preview_review(rev: dict) -> None:
    movie = rev["movie"]
    path = rev["path"]
    
    if not path.exists():
        print(color("Error: File does not exist.", RED))
        return
        
    try:
        raw = path.read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        body = parts[2] if len(parts) >= 3 else raw
        
        # Split body into sections
        sections = {}
        current_section = ""
        for line in body.splitlines():
            if line.strip().startswith("## "):
                current_section = line.strip().removeprefix("## ").strip()
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
                
        primer_text = "\n".join(sections.get("Primer", []))
        review_text = "\n".join(sections.get("Review", []))
        
        primer_words = len(primer_text.split())
        review_words = len(review_text.split())
        
        print_title(f"Quick Look: {movie.title} ({movie.year})")
        print(f"Status:          {get_status_color_tag(rev['status'])}")
        print(f"Enjoyment:       {movie.enjoyment_rating or 'TBD'}")
        print(f"Filmmaking:      {movie.filmmaking_rating or 'TBD'}")
        print(f"Word Counts:     Primer: {primer_words} words | Review: {review_words} words")
        print(f"Last Modified:   {datetime.datetime.fromtimestamp(rev['last_modified']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"File Path:       {path}")
        print("-" * 60)
        
        print(color("## Primer Preview:", BOLD + ";" + CYAN))
        primer_lines = [l for l in primer_text.splitlines() if l.strip()]
        for line in primer_lines[:5]:
            print(f"  {line}")
        if len(primer_lines) > 5:
            print(color("  ...", DIM))
            
        print()
        print(color("## Review Preview:", BOLD + ";" + CYAN))
        review_lines = [l for l in review_text.splitlines() if l.strip()]
        for line in review_lines[:5]:
            print(f"  {line}")
        if len(review_lines) > 5:
            print(color("  ...", DIM))
            
        print("-" * 60)
    except Exception as e:
        print(color(f"Error reading preview: {e}", RED))

def get_status_color_tag(status: str) -> str:
    if status == "Reviewed":
        return color("[Reviewed / Published]", GREEN)
    elif status == "In Progress":
        return color("[In Progress]", YELLOW)
    elif status == "Draft":
        return color("[Draft / Not Started]", DIM)
    return color(f"[{status}]", RED)

def select_from_list(reviews: list[dict], title: str) -> dict | None:
    if not reviews:
        print_title(title)
        print("No movies found.")
        input("\nPress Enter to return...")
        return None

    page_size = 10
    total = len(reviews)
    num_pages = (total + page_size - 1) // page_size if total > 0 else 1
    current_page = 0
    
    while True:
        print_title(title)
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, total)
        
        print(f"Page {current_page + 1} of {num_pages} ({total} movies total)")
        print("-" * 60)
        
        page_reviews = reviews[start_idx:end_idx]
        for i, rev in enumerate(page_reviews):
            item_num = i + 1
            movie = rev["movie"]
            status = rev["status"]
            year = movie.year
            status_tag = get_status_color_tag(status)
            enjoyment = movie.enjoyment_rating or "TBD"
            filmmaking = movie.filmmaking_rating or "TBD"
            
            print(f"[{item_num:2d}] {movie.title} ({year}) - {status_tag}")
            print(f"     Enjoyment: {enjoyment} | Filmmaking: {filmmaking} | Slug: {movie.slug}")
            
        print("-" * 60)
        
        nav_options = []
        if current_page > 0:
            nav_options.append(color("p: Prev Page", CYAN))
        if current_page < num_pages - 1:
            nav_options.append(color("n: Next Page", CYAN))
        nav_options.append(color("q: Back to Main Menu", RED))
        
        print(" | ".join(nav_options))
        choice = input(color("Select item number or navigation: ", BOLD)).strip().lower()
        
        if choice == 'q':
            return None
        elif choice == 'n' and current_page < num_pages - 1:
            current_page += 1
        elif choice == 'p' and current_page > 0:
            current_page -= 1
        else:
            try:
                num = int(choice)
                if 1 <= num <= len(page_reviews):
                    return page_reviews[num - 1]
                else:
                    print(color("Invalid selection. Please choose a number on this page.", RED))
                    input("Press Enter to continue...")
            except ValueError:
                print(color("Invalid input. Please try again.", RED))
                input("Press Enter to continue...")

def create_new_review_flow() -> bool:
    print_title("Create a New Review")
    title = input(color("Movie Title (required): ", BOLD)).strip()
    if not title:
        print(color("Title is required. Cancelled.", RED))
        input("Press Enter to continue...")
        return False
        
    year = input(color("Release Year (required): ", BOLD)).strip()
    if not year:
        print(color("Year is required. Cancelled.", RED))
        input("Press Enter to continue...")
        return False
        
    enjoyment = input("Enjoyment rating [TBD]: ").strip() or "TBD"
    filmmaking = input("Filmmaking rating [TBD]: ").strip() or "TBD"
    
    reviewed_input = input("Mark as reviewed? (y/n) [n]: ").strip().lower()
    reviewed = "true" if reviewed_input in ("y", "yes") else "false"
    
    slug = slugify(title)
    path = CONTENT_DIR / f"{slug}.md"
    if path.exists():
        print(color(f"Error: Review draft already exists at {path}", RED))
        input("Press Enter to continue...")
        return False
        
    try:
        CONTENT_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(
            render_review_template(
                title=title,
                slug=slug,
                tmdb_title=title,
                year=year,
                enjoyment_rating=enjoyment,
                filmmaking_rating=filmmaking,
                reviewed=reviewed,
            ),
            encoding="utf-8",
        )
        print(color(f"\nSuccessfully created new review: {path}", GREEN))
        
        # Ask to open in editor
        open_now = input("Would you like to open it in Texodus now? (y/n) [y]: ").strip().lower()
        if open_now in ("", "y", "yes"):
            open_in_texodus(path)
            
        rebuild_site()
        input("\nPress Enter to continue...")
        return True
    except Exception as e:
        print(color(f"Error creating review: {e}", RED))
        input("Press Enter to continue...")
        return False

def handle_review_actions(rev: dict) -> bool:
    path = rev["path"]
    
    while True:
        # Reload movie content to ensure freshness
        movie = load_movie(path)
        rev["movie"] = movie
        rev["status"] = get_status(movie, path)
        rev["last_modified"] = path.stat().st_mtime
        
        print_title(f"MANAGE: {movie.title} ({movie.year})")
        print(f"Status:          {get_status_color_tag(rev['status'])}")
        print(f"Enjoyment:       {movie.enjoyment_rating or 'TBD'}")
        print(f"Filmmaking:      {movie.filmmaking_rating or 'TBD'}")
        print(f"File Path:       {path}")
        print("-" * 60)
        print("1. Quick Look (Preview details & word count)")
        print("2. Open in Texodus (Auto-detects editor / opens in default app)")
        print("3. Toggle Reviewed / Published Status")
        print("4. Edit Ratings (Enjoyment & Filmmaking)")
        print("5. Rebuild static site")
        print("6. Back to lists")
        print("-" * 60)
        
        choice = input(color("Selection: ", BOLD)).strip()
        if choice == '1':
            preview_review(rev)
            input("Press Enter to return...")
        elif choice == '2':
            open_in_texodus(path)
            input("Press Enter to return...")
        elif choice == '3':
            new_val = not movie.reviewed
            if update_review_metadata(path, {"reviewed": new_val}):
                print(color(f"Reviewed status toggled to {new_val}.", GREEN))
                rebuild_site()
            input("Press Enter to return...")
        elif choice == '4':
            enjoy = input(f"New enjoyment rating [{movie.enjoyment_rating}]: ").strip() or movie.enjoyment_rating
            film = input(f"New filmmaking rating [{movie.filmmaking_rating}]: ").strip() or movie.filmmaking_rating
            if update_review_metadata(path, {"enjoyment_rating": enjoy, "filmmaking_rating": film}):
                print(color("Ratings updated successfully.", GREEN))
                rebuild_site()
            input("Press Enter to return...")
        elif choice == '5':
            rebuild_site()
            input("Press Enter to return...")
        elif choice == '6':
            return True
        else:
            print(color("Invalid choice. Try again.", RED))
            input("Press Enter to continue...")

def run_reviews_menu() -> None:
    while True:
        reviews = load_all_reviews()
        drafts = [r for r in reviews if r["status"] == "Draft"]
        in_progress = [r for r in reviews if r["status"] == "In Progress"]
        reviewed = [r for r in reviews if r["status"] == "Reviewed"]
        
        print_title("THE PROLOG - REVIEW MANAGER")
        print(f"1. Search Reviews (by title/slug)")
        print(f"2. List Drafts / Not Started ({len(drafts)} movies)")
        print(f"3. List In Progress ({len(in_progress)} movies)")
        print(f"4. List Reviewed / Published ({len(reviewed)} movies)")
        print(f"5. Create a New Review Draft")
        print(f"6. Back to Main Menu")
        print("-" * 60)
        
        choice = input(color("Selection: ", BOLD)).strip()
        if choice == '1':
            query = input("Search query (title or slug): ").strip()
            if query:
                # Find partial matches
                matches = []
                for r in reviews:
                    if query.lower() in r["movie"].title.lower() or query.lower() in r["movie"].slug.lower():
                        matches.append(r)
                selected = select_from_list(matches, f"Search Results for '{query}'")
                if selected:
                    handle_review_actions(selected)
        elif choice == '2':
            selected = select_from_list(drafts, "DRAFTS / NOT STARTED")
            if selected:
                handle_review_actions(selected)
        elif choice == '3':
            selected = select_from_list(in_progress, "IN PROGRESS REVIEWS")
            if selected:
                handle_review_actions(selected)
        elif choice == '4':
            selected = select_from_list(reviewed, "REVIEWED / PUBLISHED")
            if selected:
                handle_review_actions(selected)
        elif choice == '5':
            create_new_review_flow()
        elif choice == '6':
            break
        else:
            print(color("Invalid choice. Try again.", RED))
            input("Press Enter to continue...")

# --- Collection Flows & Menus ---

def select_collection_from_list(collections: list[dict], title: str) -> dict | None:
    if not collections:
        print_title(title)
        print("No collections found.")
        input("\nPress Enter to return...")
        return None

    page_size = 10
    total = len(collections)
    num_pages = (total + page_size - 1) // page_size if total > 0 else 1
    current_page = 0
    
    while True:
        print_title(title)
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, total)
        
        print(f"Page {current_page + 1} of {num_pages} ({total} collections total)")
        print("-" * 60)
        
        page_cols = collections[start_idx:end_idx]
        for i, item in enumerate(page_cols):
            item_num = i + 1
            col = item["collection"]
            print(f"[{item_num:2d}] {col.title} - {len(col.movies)} movies")
            print(f"     Teaser: {col.teaser}")
            print(f"     Slug:   {col.slug}")
            
        print("-" * 60)
        
        nav_options = []
        if current_page > 0:
            nav_options.append(color("p: Prev Page", CYAN))
        if current_page < num_pages - 1:
            nav_options.append(color("n: Next Page", CYAN))
        nav_options.append(color("q: Back to Collections Menu", RED))
        
        print(" | ".join(nav_options))
        choice = input(color("Select item number or navigation: ", BOLD)).strip().lower()
        
        if choice == 'q':
            return None
        elif choice == 'n' and current_page < num_pages - 1:
            current_page += 1
        elif choice == 'p' and current_page > 0:
            current_page -= 1
        else:
            try:
                num = int(choice)
                if 1 <= num <= len(page_cols):
                    return page_cols[num - 1]
                else:
                    print(color("Invalid selection. Please choose a number on this page.", RED))
                    input("Press Enter to continue...")
            except ValueError:
                print(color("Invalid input. Please try again.", RED))
                input("Press Enter to continue...")

def show_collection_details(col: CollectionContent) -> None:
    print_title(f"Details: {col.title}")
    print(f"Slug:    {col.slug}")
    print(f"Teaser:  {col.teaser}")
    print("-" * 60)
    print("Movies:")
    reviews = load_all_reviews()
    reviews_by_slug = {r["movie"].slug: r for r in reviews}
    for idx, movie_slug in enumerate(col.movies):
        if movie_slug in reviews_by_slug:
            r = reviews_by_slug[movie_slug]
            m = r["movie"]
            status_tag = get_status_color_tag(r["status"])
            print(f"  [{idx + 1:2d}] {m.title} ({m.year}) - {status_tag} (slug: {movie_slug})")
        else:
            print(f"  [{idx + 1:2d}] {color(f'Warning: Review draft/file not found for slug: {movie_slug}', RED)}")

def preview_collection(col: CollectionContent, path: Path) -> None:
    print_title(f"Preview: {col.title}")
    print(f"Teaser: {col.teaser}")
    print("-" * 60)
    try:
        raw = path.read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        body = parts[2] if len(parts) >= 3 else raw
        
        body_lines = body.strip().splitlines()
        print(color("## Overview Preview:", BOLD + ";" + CYAN))
        for line in body_lines[:20]:
            print(f"  {line}")
        if len(body_lines) > 20:
            print(color("  ...", DIM))
    except Exception as e:
        print(color(f"Error reading collection preview: {e}", RED))

def edit_collection_metadata_flow(col: CollectionContent, path: Path) -> None:
    print_title(f"Edit Metadata: {col.title}")
    new_title = input(f"New Title [{col.title}]: ").strip() or col.title
    new_teaser = input(f"New Teaser [{col.teaser}]: ").strip() or col.teaser
    
    updates = {}
    if new_title != col.title:
        updates["title"] = new_title
    if new_teaser != col.teaser:
        updates["teaser"] = new_teaser
        
    if updates:
        if update_collection_metadata_file(path, updates):
            print(color("Collection metadata updated successfully.", GREEN))
            rebuild_site()
        else:
            print(color("Failed to update collection metadata.", RED))
    else:
        print("No changes made.")
    input("\nPress Enter to continue...")

def manage_collection_movies_flow(col: CollectionContent, path: Path) -> None:
    while True:
        col = load_collection(path)
        print_title(f"Manage Movies in: {col.title}")
        print("Current Movies:")
        
        # Load all movie slugs for validation
        available_slugs = {p.stem for p in CONTENT_DIR.glob("*.md")}
        
        for idx, m_slug in enumerate(col.movies):
            exists_str = "" if m_slug in available_slugs else color(" [Does not exist!]", RED)
            print(f"  [{idx + 1:2d}] {m_slug}{exists_str}")
        print("-" * 60)
        print("1. Add a movie to this collection")
        print("2. Remove a movie from this collection")
        print("3. Reorder movies in this collection")
        print("4. Back to Collection Menu")
        print("-" * 60)
        
        choice = input(color("Selection: ", BOLD)).strip()
        if choice == '1':
            print("\nAvailable movie reviews (first 20 slugs):")
            sorted_slugs = sorted(list(available_slugs))
            print(", ".join(sorted_slugs[:20]) + ("..." if len(sorted_slugs) > 20 else ""))
            new_slug = input("Enter movie slug to add: ").strip()
            if not new_slug:
                continue
            if new_slug in col.movies:
                print(color(f"Movie slug '{new_slug}' is already in the collection.", YELLOW))
            elif new_slug in available_slugs:
                new_movies = list(col.movies) + [new_slug]
                if update_collection_metadata_file(path, {"movies": new_movies}):
                    print(color(f"Added '{new_slug}' to collection.", GREEN))
                    rebuild_site()
            else:
                matches = [s for s in available_slugs if new_slug in s]
                print(color(f"Slug '{new_slug}' not found.", RED))
                if matches:
                    print(f"Did you mean: {', '.join(matches[:5])}?")
                force_add = input("Add anyway? (y/n) [n]: ").strip().lower()
                if force_add in ("y", "yes"):
                    new_movies = list(col.movies) + [new_slug]
                    if update_collection_metadata_file(path, {"movies": new_movies}):
                        print(color(f"Added '{new_slug}' to collection.", GREEN))
                        rebuild_site()
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            if not col.movies:
                print(color("No movies in collection to remove.", YELLOW))
                input("\nPress Enter to continue...")
                continue
            remove_idx_str = input("Enter the number of the movie to remove: ").strip()
            try:
                idx = int(remove_idx_str) - 1
                if 0 <= idx < len(col.movies):
                    removed = col.movies[idx]
                    new_movies = list(col.movies)
                    new_movies.pop(idx)
                    if update_collection_metadata_file(path, {"movies": new_movies}):
                        print(color(f"Removed '{removed}' from collection.", GREEN))
                        rebuild_site()
                else:
                    print(color("Invalid index.", RED))
            except ValueError:
                print(color("Invalid input.", RED))
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            if len(col.movies) < 2:
                print(color("Need at least 2 movies to reorder.", YELLOW))
                input("\nPress Enter to continue...")
                continue
            print("\nEnter new ordered indexes separated by spaces or commas.")
            print(f"Example: '2 1 3' to swap the first and second movies in a list of 3.")
            order_str = input("New order: ").strip()
            if not order_str:
                continue
            import re
            parts = re.split(r'[\s,]+', order_str)
            try:
                idxs = [int(p) - 1 for p in parts if p]
                if len(idxs) != len(col.movies) or set(idxs) != set(range(len(col.movies))):
                    print(color(f"Error: You must specify exactly all indexes from 1 to {len(col.movies)}.", RED))
                else:
                    new_movies = [col.movies[i] for i in idxs]
                    if update_collection_metadata_file(path, {"movies": new_movies}):
                        print(color("Reordered movies successfully.", GREEN))
                        rebuild_site()
            except ValueError:
                print(color("Error: Invalid numbers specified.", RED))
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            break

def create_new_collection_flow() -> bool:
    print_title("Create a New Collection")
    title = input(color("Collection Title (required): ", BOLD)).strip()
    if not title:
        print(color("Title is required. Cancelled.", RED))
        input("Press Enter to continue...")
        return False
        
    teaser = input(color("Teaser/Short Description (required): ", BOLD)).strip()
    if not teaser:
        print(color("Teaser is required. Cancelled.", RED))
        input("Press Enter to continue...")
        return False
        
    slug = slugify(title)
    path = COLLECTIONS_DIR / f"{slug}.md"
    if path.exists():
        print(color(f"Error: Collection already exists at {path}", RED))
        input("Press Enter to continue...")
        return False
        
    # Prompt for movies
    available_slugs = {p.stem for p in CONTENT_DIR.glob("*.md")}
    movies = []
    print("\nEnter movie slugs to include in this collection.")
    print("Type a slug and press Enter. Leave empty and press Enter when finished.")
    while True:
        val = input(f"Movie slug (already added: {len(movies)}): ").strip()
        if not val:
            break
        if val in available_slugs:
            movies.append(val)
            print(f"Added: {val}")
        else:
            # Find closest matches
            matches = [s for s in available_slugs if val in s]
            print(color(f"Slug '{val}' not found.", RED))
            if matches:
                print(f"Did you mean: {', '.join(matches[:5])}?")
            add_anyway = input("Add anyway? (y/n) [n]: ").strip().lower()
            if add_anyway in ("y", "yes"):
                movies.append(val)
                print(f"Added: {val}")

    try:
        COLLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
        front_matter = [
            f"title: {title}",
            f"slug: {slug}",
            f"teaser: {teaser}",
            "movies:",
        ]
        for m in movies:
            front_matter.append(f"  - {m}")
        front_matter_str = "\n".join(front_matter)
        
        content = f"""---
{front_matter_str}
---

## Overview

Add the collection overview description here. Markdown is supported.
"""
        path.write_text(content, encoding="utf-8")
        print(color(f"\nSuccessfully created new collection: {path}", GREEN))
        
        open_now = input("Would you like to open it in Texodus now? (y/n) [y]: ").strip().lower()
        if open_now in ("", "y", "yes"):
            open_in_texodus(path)
            
        rebuild_site()
        input("\nPress Enter to continue...")
        return True
    except Exception as e:
        print(color(f"Error creating collection: {e}", RED))
        input("Press Enter to continue...")
        return False

def handle_collection_actions(col: CollectionContent, path: Path) -> bool:
    while True:
        # Reload collection content to ensure freshness
        col = load_collection(path)
        
        print_title(f"MANAGE COLLECTION: {col.title}")
        print(f"Slug:            {col.slug}")
        print(f"Teaser:          {col.teaser}")
        print(f"Movies count:    {len(col.movies)}")
        print(f"File Path:       {path}")
        print("-" * 60)
        print("1. Show Details & Movie Statuses")
        print("2. Open in Texodus")
        print("3. Preview Collection Teaser & Overview")
        print("4. Edit Title / Teaser")
        print("5. Manage Movies (Add / Remove / Reorder)")
        print("6. Rebuild static site")
        print("7. Back to collections list")
        print("-" * 60)
        
        choice = input(color("Selection: ", BOLD)).strip()
        if choice == '1':
            show_collection_details(col)
            input("\nPress Enter to return...")
        elif choice == '2':
            open_in_texodus(path)
            input("\nPress Enter to return...")
        elif choice == '3':
            preview_collection(col, path)
            input("\nPress Enter to return...")
        elif choice == '4':
            edit_collection_metadata_flow(col, path)
        elif choice == '5':
            manage_collection_movies_flow(col, path)
        elif choice == '6':
            rebuild_site()
            input("\nPress Enter to return...")
        elif choice == '7':
            return True
        else:
            print(color("Invalid choice. Try again.", RED))
            input("Press Enter to continue...")

def run_collections_menu() -> None:
    while True:
        collections = load_all_collections()
        
        print_title("THE PROLOG - COLLECTION MANAGER")
        print(f"1. Search / List All Collections ({len(collections)} collections)")
        print(f"2. Create a New Collection")
        print(f"3. Back to Main Menu")
        print("-" * 60)
        
        choice = input(color("Selection: ", BOLD)).strip()
        if choice == '1':
            query = input("Search query (optional, title or slug): ").strip()
            matches = collections
            if query:
                matches = []
                for c in collections:
                    if query.lower() in c["collection"].title.lower() or query.lower() in c["collection"].slug.lower():
                        matches.append(c)
            selected = select_collection_from_list(matches, f"Collections Search Results")
            if selected:
                handle_collection_actions(selected["collection"], selected["path"])
        elif choice == '2':
            create_new_collection_flow()
        elif choice == '3':
            break
        else:
            print(color("Invalid choice. Try again.", RED))
            input("Press Enter to continue...")

# --- Main Interactive Loop ---

def run_interactive() -> None:
    while True:
        print_title("THE PROLOG - MANAGEMENT CLI")
        print("1. Manage Reviews")
        print("2. Manage Collections")
        print("3. Rebuild static site")
        print("4. Exit")
        print("-" * 60)
        
        choice = input(color("Selection: ", BOLD)).strip()
        if choice == '1':
            run_reviews_menu()
        elif choice == '2':
            run_collections_menu()
        elif choice == '3':
            rebuild_site()
            input("\nPress Enter to continue...")
        elif choice == '4':
            print(color("\nGoodbye!", GREEN))
            break
        else:
            print(color("Invalid choice. Try again.", RED))
            input("Press Enter to continue...")

def find_review_by_slug_or_title(slug_or_title: str, reviews: list[dict]) -> dict | None:
    for r in reviews:
        if r["movie"].slug == slug_or_title:
            return r
    for r in reviews:
        if r["movie"].title.lower() == slug_or_title.lower():
            return r
    matches = []
    for r in reviews:
        if slug_or_title.lower() in r["movie"].title.lower() or slug_or_title.lower() in r["movie"].slug.lower():
            matches.append(r)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(color(f"Multiple matches found for '{slug_or_title}':", YELLOW))
        for m in matches:
            print(f"  - {m['movie'].slug} ({m['movie'].title})")
        return None
    return None

def find_collection_by_slug_or_title(slug_or_title: str, collections: list[dict]) -> dict | None:
    for c in collections:
        if c["collection"].slug == slug_or_title:
            return c
    for c in collections:
        if c["collection"].title.lower() == slug_or_title.lower():
            return c
    matches = []
    for c in collections:
        if slug_or_title.lower() in c["collection"].title.lower() or slug_or_title.lower() in c["collection"].slug.lower():
            matches.append(c)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(color(f"Multiple matches found for '{slug_or_title}':", YELLOW))
        for m in matches:
            print(f"  - {m['collection'].slug} ({m['collection'].title})")
        return None
    return None

def main() -> None:
    # Rewrite arguments for backward compatibility (legacy top-level review commands)
    if len(sys.argv) > 1 and sys.argv[1] not in ("review", "collection", "-h", "--help"):
        legacy_cmds = {"list", "status", "open", "update", "preview", "create"}
        if sys.argv[1] in legacy_cmds:
            sys.argv.insert(1, "review")

    parser = argparse.ArgumentParser(description="The Prolog Review & Collection Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand group")
    
    # Review subparser group
    review_parser = subparsers.add_parser("review", help="Manage movie reviews")
    review_subparsers = review_parser.add_subparsers(dest="subcommand", help="Review subcommand")
    
    # Review List
    r_list = review_subparsers.add_parser("list", help="List reviews")
    r_list.add_argument("--status", choices=["draft", "in-progress", "reviewed"], help="Filter by status")
    r_list.add_argument("--search", help="Search term (title or slug)")
    
    # Review Status
    r_status = review_subparsers.add_parser("status", help="Get status of a review")
    r_status.add_argument("slug_or_title", help="Review slug or title")
    
    # Review Open
    r_open = review_subparsers.add_parser("open", help="Open a review in editor")
    r_open.add_argument("slug_or_title", help="Review slug or title")
    
    # Review Update
    r_update = review_subparsers.add_parser("update", help="Update review metadata")
    r_update.add_argument("slug_or_title", help="Review slug or title")
    r_update.add_argument("--enjoyment", help="Set enjoyment rating")
    r_update.add_argument("--filmmaking", help="Set filmmaking rating")
    r_update.add_argument("--reviewed", choices=["true", "false"], help="Set reviewed status")
    r_update.add_argument("--rebuild", action="store_true", help="Rebuild the site after update")
    
    # Review Preview
    r_preview = review_subparsers.add_parser("preview", help="Preview review content")
    r_preview.add_argument("slug_or_title", help="Review slug or title")
    
    # Review Create
    r_create = review_subparsers.add_parser("create", help="Create a new review")
    r_create.add_argument("--title", required=True, help="Movie title")
    r_create.add_argument("--year", required=True, help="Release year")
    r_create.add_argument("--enjoyment", default="TBD", help="Enjoyment rating")
    r_create.add_argument("--filmmaking", default="TBD", help="Filmmaking rating")
    r_create.add_argument("--reviewed", action="store_true", help="Mark as reviewed")
    r_create.add_argument("--rebuild", action="store_true", help="Rebuild the site after creation")
    
    # Collection subparser group
    collection_parser = subparsers.add_parser("collection", help="Manage movie collections")
    collection_subparsers = collection_parser.add_subparsers(dest="subcommand", help="Collection subcommand")
    
    # Collection List
    c_list = collection_subparsers.add_parser("list", help="List collections")
    c_list.add_argument("--search", help="Search term (title or slug)")
    
    # Collection Status
    c_status = collection_subparsers.add_parser("status", help="Get status of a collection")
    c_status.add_argument("slug_or_title", help="Collection slug or title")
    
    # Collection Open
    c_open = collection_subparsers.add_parser("open", help="Open a collection in editor")
    c_open.add_argument("slug_or_title", help="Collection slug or title")
    
    # Collection Update
    c_update = collection_subparsers.add_parser("update", help="Update collection metadata")
    c_update.add_argument("slug_or_title", help="Collection slug or title")
    c_update.add_argument("--title", help="Set collection title")
    c_update.add_argument("--teaser", help="Set collection teaser")
    c_update.add_argument("--movies", help="Set movie slugs (comma-separated, replaces current list)")
    c_update.add_argument("--add-movies", help="Add movie slugs to collection (comma-separated)")
    c_update.add_argument("--remove-movies", help="Remove movie slugs from collection (comma-separated)")
    c_update.add_argument("--rebuild", action="store_true", help="Rebuild the site after update")
    
    # Collection Preview
    c_preview = collection_subparsers.add_parser("preview", help="Preview collection content")
    c_preview.add_argument("slug_or_title", help="Collection slug or title")
    
    # Collection Create
    c_create = collection_subparsers.add_parser("create", help="Create a new collection")
    c_create.add_argument("--title", help="Collection title")
    c_create.add_argument("--teaser", help="Collection teaser")
    c_create.add_argument("--movies", help="Movie slugs (comma-separated list)")
    c_create.add_argument("--slug", help="Collection slug (optional, generated from title if not set)")
    c_create.add_argument("--force", action="store_true", help="Overwrite existing collection")
    c_create.add_argument("--rebuild", action="store_true", help="Rebuild the site after creation")
    
    args = parser.parse_args()
    
    if args.command is None:
        run_interactive()
        return
        
    if args.command == "review":
        if args.subcommand is None:
            review_parser.print_help()
            sys.exit(0)
            
        reviews = load_all_reviews()
        
        if args.subcommand == "list":
            filtered = reviews
            if args.status:
                status_map = {"draft": "Draft", "in-progress": "In Progress", "reviewed": "Reviewed"}
                filtered = [r for r in filtered if r["status"] == status_map[args.status]]
            if args.search:
                filtered = [r for r in filtered if args.search.lower() in r["movie"].title.lower() or args.search.lower() in r["movie"].slug.lower()]
                
            for r in filtered:
                movie = r["movie"]
                print(f"{movie.slug:<40} {get_status_color_tag(r['status']):<35} {movie.title} ({movie.year})")
                
        elif args.subcommand in ("status", "open", "update", "preview"):
            target = find_review_by_slug_or_title(args.slug_or_title, reviews)
            if not target:
                print(color(f"Error: Review '{args.slug_or_title}' not found.", RED))
                sys.exit(1)
                
            if args.subcommand == "status":
                movie = target["movie"]
                print(f"Title:         {movie.title} ({movie.year})")
                print(f"Slug:          {movie.slug}")
                print(f"Status:        {get_status_color_tag(target['status'])}")
                print(f"Enjoyment:     {movie.enjoyment_rating or 'TBD'}")
                print(f"Filmmaking:    {movie.filmmaking_rating or 'TBD'}")
                print(f"Last Modified: {datetime.datetime.fromtimestamp(target['last_modified']).strftime('%Y-%m-%d %H:%M:%S')}")
                
            elif args.subcommand == "open":
                open_in_texodus(target["path"])
                
            elif args.subcommand == "preview":
                movie = target["movie"]
                path = target["path"]
                raw = path.read_text(encoding="utf-8")
                parts = raw.split("---", 2)
                body = parts[2] if len(parts) >= 3 else raw
                
                print(color(f"=== {movie.title} ({movie.year}) - {target['status']} ===", BOLD + ";" + BLUE))
                body_lines = body.strip().splitlines()
                for line in body_lines[:25]:
                    print(line)
                if len(body_lines) > 25:
                    print(color("...", DIM))
                    
            elif args.subcommand == "update":
                updates = {}
                if args.enjoyment is not None:
                    updates["enjoyment_rating"] = args.enjoyment
                if args.filmmaking is not None:
                    updates["filmmaking_rating"] = args.filmmaking
                if args.reviewed is not None:
                    updates["reviewed"] = args.reviewed == "true"
                    
                if not updates:
                    print(color("No updates specified.", YELLOW))
                    return
                    
                if update_review_metadata(target["path"], updates):
                    print(color(f"Successfully updated metadata for {target['movie'].title}.", GREEN))
                    if args.rebuild:
                        rebuild_site()
                else:
                    sys.exit(1)
                    
        elif args.subcommand == "create":
            slug = slugify(args.title)
            path = CONTENT_DIR / f"{slug}.md"
            if path.exists():
                print(color(f"Error: Review draft already exists at {path}", RED))
                sys.exit(1)
                
            try:
                CONTENT_DIR.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    render_review_template(
                        title=args.title,
                        slug=slug,
                        tmdb_title=args.title,
                        year=args.year,
                        enjoyment_rating=args.enjoyment,
                        filmmaking_rating=args.filmmaking,
                        reviewed="true" if args.reviewed else "false",
                    ),
                    encoding="utf-8",
                )
                print(color(f"Successfully created new review: {path}", GREEN))
                if args.rebuild:
                    rebuild_site()
            except Exception as e:
                print(color(f"Error creating review: {e}", RED))
                sys.exit(1)

    elif args.command == "collection":
        if args.subcommand is None:
            collection_parser.print_help()
            sys.exit(0)
            
        collections = load_all_collections()
        
        if args.subcommand == "list":
            filtered = collections
            if args.search:
                filtered = [c for c in collections if args.search.lower() in c["collection"].title.lower() or args.search.lower() in c["collection"].slug.lower()]
            for c in filtered:
                col = c["collection"]
                print(f"{col.slug:<30} ({len(col.movies)} movies) {col.title}")
                
        elif args.subcommand in ("status", "open", "update", "preview"):
            target = find_collection_by_slug_or_title(args.slug_or_title, collections)
            if not target:
                print(color(f"Error: Collection '{args.slug_or_title}' not found.", RED))
                sys.exit(1)
                
            col = target["collection"]
            path = target["path"]
            
            if args.subcommand == "status":
                print(f"Title:         {col.title}")
                print(f"Slug:          {col.slug}")
                print(f"Teaser:        {col.teaser}")
                print(f"File Path:     {path}")
                print(f"Last Modified: {datetime.datetime.fromtimestamp(target['last_modified']).strftime('%Y-%m-%d %H:%M:%S')}")
                print("Movies:")
                reviews = load_all_reviews()
                reviews_by_slug = {r["movie"].slug: r for r in reviews}
                for idx, movie_slug in enumerate(col.movies):
                    if movie_slug in reviews_by_slug:
                        r = reviews_by_slug[movie_slug]
                        m = r["movie"]
                        status_tag = get_status_color_tag(r["status"])
                        print(f"  - {m.title} ({m.year}) - {status_tag} (slug: {movie_slug})")
                    else:
                        print(f"  - {movie_slug} {color('[Review draft/file not found]', RED)}")
                        
            elif args.subcommand == "open":
                open_in_texodus(path)
                
            elif args.subcommand == "preview":
                print(color(f"=== Collection Preview: {col.title} ===", BOLD + ";" + BLUE))
                print(f"Teaser: {col.teaser}")
                print("-" * 60)
                raw = path.read_text(encoding="utf-8")
                parts = raw.split("---", 2)
                body = parts[2] if len(parts) >= 3 else raw
                body_lines = body.strip().splitlines()
                for line in body_lines[:25]:
                    print(line)
                if len(body_lines) > 25:
                    print(color("...", DIM))
                    
            elif args.subcommand == "update":
                updates = {}
                if args.title is not None:
                    updates["title"] = args.title
                if args.teaser is not None:
                    updates["teaser"] = args.teaser
                
                # Handling movie list modifications
                current_movies = list(col.movies)
                if args.movies is not None:
                    current_movies = [m.strip() for m in args.movies.split(",") if m.strip()]
                    
                if args.add_movies is not None:
                    to_add = [m.strip() for m in args.add_movies.split(",") if m.strip()]
                    for m in to_add:
                        if m not in current_movies:
                            current_movies.append(m)
                            
                if args.remove_movies is not None:
                    to_remove = [m.strip() for m in args.remove_movies.split(",") if m.strip()]
                    current_movies = [m for m in current_movies if m not in to_remove]
                
                if args.movies is not None or args.add_movies is not None or args.remove_movies is not None:
                    # Validate new slugs
                    available_slugs = {p.stem for p in CONTENT_DIR.glob("*.md")}
                    invalid = [s for s in current_movies if s not in available_slugs]
                    if invalid:
                        print(color(f"Warning: The following movie slugs were not found: {', '.join(invalid)}", YELLOW))
                    updates["movies"] = current_movies
                    
                if not updates:
                    print(color("No updates specified.", YELLOW))
                    return
                    
                if update_collection_metadata_file(path, updates):
                    print(color(f"Successfully updated metadata for collection '{col.title}'.", GREEN))
                    if args.rebuild:
                        rebuild_site()
                else:
                    sys.exit(1)
                    
        elif args.subcommand == "create":
            title = args.title
            teaser = args.teaser
            
            if not title:
                print(color("Error: --title is required for collection creation.", RED))
                sys.exit(1)
            if not teaser:
                print(color("Error: --teaser is required for collection creation.", RED))
                sys.exit(1)
                
            slug = args.slug or slugify(title)
            path = COLLECTIONS_DIR / f"{slug}.md"
            if path.exists() and not args.force:
                print(color(f"Error: Collection already exists at {path}. Use --force to overwrite.", RED))
                sys.exit(1)
                
            movies = []
            if args.movies:
                movies = [m.strip() for m in args.movies.split(",") if m.strip()]
                available_slugs = {p.stem for p in CONTENT_DIR.glob("*.md")}
                invalid = [s for s in movies if s not in available_slugs]
                if invalid:
                    print(color(f"Warning: The following movie slugs were not found: {', '.join(invalid)}", YELLOW))
                    
            try:
                COLLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
                front_matter = [
                    f"title: {title}",
                    f"slug: {slug}",
                    f"teaser: {teaser}",
                    "movies:",
                ]
                for m in movies:
                    front_matter.append(f"  - {m}")
                front_matter_str = "\n".join(front_matter)
                
                content = f"""---
{front_matter_str}
---

## Overview

Add the collection overview description here. Markdown is supported.
"""
                path.write_text(content, encoding="utf-8")
                print(color(f"Successfully created collection: {path}", GREEN))
                if args.rebuild:
                    rebuild_site()
            except Exception as e:
                print(color(f"Error creating collection: {e}", RED))
                sys.exit(1)

if __name__ == "__main__":
    main()
