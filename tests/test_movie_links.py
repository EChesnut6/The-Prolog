import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.content import convert_wiki_links
from src.render import resolve_movie_links

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
        resolved = resolve_movie_links(html, "root", all_slugs)
        self.assertIn('href="public/reviews/12-angry-men.html"', resolved)
        self.assertIn('href="public/reviews/casablanca.html"', resolved)

        # Public pages (e.g., search) should resolve to reviews/
        resolved = resolve_movie_links(html, "public", all_slugs)
        self.assertIn('href="reviews/12-angry-men.html"', resolved)
        self.assertIn('href="reviews/casablanca.html"', resolved)

        # Individual reviews (already inside reviews/) should resolve to local/relative folder path (empty prefix)
        resolved = resolve_movie_links(html, "review", all_slugs)
        self.assertIn('href="12-angry-men.html"', resolved)
        self.assertIn('href="casablanca.html"', resolved)

        # Collection pages (inside collections/) should resolve to ../reviews/
        resolved = resolve_movie_links(html, "collection", all_slugs)
        self.assertIn('href="../reviews/12-angry-men.html"', resolved)
        self.assertIn('href="../reviews/casablanca.html"', resolved)

    def test_fallback_to_coming_soon(self):
        all_slugs = {"casablanca"}
        
        # 12 Angry Men does not exist, so it should redirect to coming soon page relative to each page type
        html = '<a href="12-angry-men.md">12 Angry Men</a> and <a href="casablanca.md">Casablanca</a>'
        
        resolved_root = resolve_movie_links(html, "root", all_slugs)
        self.assertIn('href="public/coming-soon.html"', resolved_root)
        self.assertIn('href="public/reviews/casablanca.html"', resolved_root)

        resolved_review = resolve_movie_links(html, "review", all_slugs)
        self.assertIn('href="../coming-soon.html"', resolved_review)
        self.assertIn('href="casablanca.html"', resolved_review)

        resolved_collection = resolve_movie_links(html, "collection", all_slugs)
        self.assertIn('href="../coming-soon.html"', resolved_collection)
        self.assertIn('href="../reviews/casablanca.html"', resolved_collection)

if __name__ == "__main__":
    unittest.main()
