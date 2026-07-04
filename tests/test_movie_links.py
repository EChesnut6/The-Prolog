import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.content import convert_wiki_links
from src.render import resolve_links

class TestMovieLinks(unittest.TestCase):
    def test_convert_wiki_links(self):
        # Test basic WikiLink conversion
        text = "Check out [[12 Angry Men]]"
        self.assertEqual(convert_wiki_links(text), "Check out [12 Angry Men](12-angry-men.md)")
        
        # Test WikiLink with custom anchor text
        text = "This is a [[12-angry-men|classic movie]]"
        self.assertEqual(convert_wiki_links(text), "This is a [classic movie](12-angry-men.md)")
        
        # Test WikiLink with .md file extension in target
        text = "Reference to [[casablanca.md]]"
        self.assertEqual(convert_wiki_links(text), "Reference to [casablanca.md](casablanca.md)")

        # Test WikiLink with .md extension and custom anchor
        text = "Reference to [[casablanca.md|Casablanca]]"
        self.assertEqual(convert_wiki_links(text), "Reference to [Casablanca](casablanca.md)")

        # Test multiple WikiLinks
        text = "Compare [[12-angry-men]] with [[casablanca|Casablanca]]"
        self.assertEqual(
            convert_wiki_links(text), 
            "Compare [12-angry-men](12-angry-men.md) with [Casablanca](casablanca.md)"
        )

    def test_resolve_movie_links(self):
        all_slugs = {"12-angry-men", "casablanca", "vanilla-sky"}
        
        # Root index links should resolve to public/reviews/
        html = '<a href="12-angry-men.md">12 Angry Men</a> and <a href="./casablanca.md">Casablanca</a>'
        resolved = resolve_links(html, "root", all_slugs, set())
        self.assertIn('href="public/reviews/12-angry-men.html"', resolved)
        self.assertIn('href="public/reviews/casablanca.html"', resolved)

        # Public pages (e.g., search) should resolve to reviews/
        resolved = resolve_links(html, "public", all_slugs, set())
        self.assertIn('href="reviews/12-angry-men.html"', resolved)
        self.assertIn('href="reviews/casablanca.html"', resolved)

        # Individual reviews (already inside reviews/) should resolve to local/relative folder path (empty prefix)
        resolved = resolve_links(html, "review", all_slugs, set())
        self.assertIn('href="12-angry-men.html"', resolved)
        self.assertIn('href="casablanca.html"', resolved)

        # Collection pages (inside collections/) should resolve to ../reviews/
        resolved = resolve_links(html, "collection", all_slugs, set())
        self.assertIn('href="../reviews/12-angry-men.html"', resolved)
        self.assertIn('href="../reviews/casablanca.html"', resolved)

    def test_fallback_to_coming_soon(self):
        all_slugs = {"casablanca"}
        
        # 12 Angry Men does not exist, so it should redirect to coming soon page relative to each page type
        html = '<a href="12-angry-men.md">12 Angry Men</a> and <a href="casablanca.md">Casablanca</a>'
        
        resolved_root = resolve_links(html, "root", all_slugs, set())
        self.assertIn('href="public/coming-soon.html"', resolved_root)
        self.assertIn('href="public/reviews/casablanca.html"', resolved_root)

        resolved_review = resolve_links(html, "review", all_slugs, set())
        self.assertIn('href="../coming-soon.html"', resolved_review)
        self.assertIn('href="casablanca.html"', resolved_review)

        resolved_collection = resolve_links(html, "collection", all_slugs, set())
        self.assertIn('href="../coming-soon.html"', resolved_collection)
        self.assertIn('href="../reviews/casablanca.html"', resolved_collection)

    def test_similar_movies_exclusion(self):
        from src.render import _get_similar_movies
        
        class MockMovie:
            def __init__(self, title, slug, year, reviewed=True):
                self.title = title
                self.slug = slug
                self.year = year
                self.reviewed = reviewed
                
        current_movie = MockMovie("Inception", "inception", "2010")
        current_metadata = {"genres": ["Sci-Fi", "Action"], "director": "Christopher Nolan"}
        
        m1 = MockMovie("Interstellar", "interstellar", "2014")
        m2 = MockMovie("Tenet", "tenet", "2020")
        m3 = MockMovie("The Matrix", "the-matrix", "1999")
        
        all_movies = [
            (m1, {"director": "Christopher Nolan", "genres": ["Sci-Fi", "Action"]}),
            (m2, {"director": "Christopher Nolan", "genres": ["Sci-Fi", "Action"]}),
            (m3, {"director": "Lana Wachowski", "genres": ["Sci-Fi", "Action"]}),
        ]
        
        # Without exclusion, Interstellar and Tenet are the most similar because of same director
        similar_no_exclude = _get_similar_movies(current_movie, current_metadata, all_movies, limit=3)
        self.assertEqual(len(similar_no_exclude), 3)
        self.assertEqual(similar_no_exclude[0]["slug"], "interstellar")
        self.assertEqual(similar_no_exclude[1]["slug"], "tenet")
        self.assertEqual(similar_no_exclude[2]["slug"], "the-matrix")
        
        # With exclusion of director movies (interstellar and tenet)
        exclude_slugs = {"interstellar", "tenet"}
        similar_with_exclude = _get_similar_movies(current_movie, current_metadata, all_movies, limit=3, exclude_slugs=exclude_slugs)
        
        # Now only The Matrix should be returned because Interstellar and Tenet are excluded
        self.assertEqual(len(similar_with_exclude), 1)
        self.assertEqual(similar_with_exclude[0]["slug"], "the-matrix")

    def test_extract_premise_section(self):
        from src.content import _extract_premise_section
        
        # Test basic premise extraction
        primer_text = """
#### The Premise
A young Manhattan insurance clerk tries to rise...

#### Essentials
Unfortunately, I wasn't able to find...
"""
        extracted = _extract_premise_section(primer_text)
        self.assertEqual(
            extracted,
            "#### The Premise\nA young Manhattan insurance clerk tries to rise..."
        )
        
        # Test premise + essentials extraction
        primer_text_2 = """
#### The Premise + Essentials
Family moves to the fictional town...

#### Vibe
It's pretty fun vibes...
"""
        extracted_2 = _extract_premise_section(primer_text_2)
        self.assertEqual(
            extracted_2,
            "#### The Premise + Essentials\nFamily moves to the fictional town..."
        )
        
        # Test missing premise section returns None
        primer_text_3 = """
#### Vibe
It's pretty fun vibes...
"""
        extracted_3 = _extract_premise_section(primer_text_3)
        self.assertIsNone(extracted_3)

if __name__ == "__main__":
    unittest.main()
