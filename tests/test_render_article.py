import json
import tempfile
import unittest
from pathlib import Path

from scripts.render_article import render_article_html, render_article_file


class RenderArticleTests(unittest.TestCase):
    def test_render_article_html_preserves_theme_cta_metadata_and_body(self):
        draft = {
            "slug": "chaos-rising-discipline",
            "title": "Discipline Before Revolt",
            "description": "A Chaos Rising field note.",
            "official_title": "Chaos Rising",
            "official_year": 2082,
            "site_anchor": "https://exodus.orsontbadger.com/#book-1",
            "body_html": "<p>Chaos Rising body.</p>",
        }

        html = render_article_html(draft)

        self.assertIn("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">", html)
        self.assertIn(".article-wrap", html)
        self.assertIn(".sticky-cta", html)
        self.assertIn(".sales-card", html)
        self.assertIn("Discipline Before Revolt", html)
        self.assertIn("Chaos Rising · 2082", html)
        self.assertIn("https://exodus.orsontbadger.com/#book-1", html)

    def test_render_article_file_writes_article_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft = {
                "slug": "chaos-rising-discipline",
                "title": "Discipline Before Revolt",
                "description": "A Chaos Rising field note.",
                "official_title": "Chaos Rising",
                "official_year": 2082,
                "site_anchor": "https://exodus.orsontbadger.com/#book-1",
                "body_html": "<p>Chaos Rising body.</p>",
            }

            article_path = render_article_file(draft, output_dir=root / "articles")

            self.assertEqual(article_path.name, "chaos-rising-discipline.html")
            self.assertIn("Discipline Before Revolt", article_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
