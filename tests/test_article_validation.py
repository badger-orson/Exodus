import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_article import validate_draft_article


def words(n):
    return " ".join(f"word{i}" for i in range(n))


class ArticleValidationTests(unittest.TestCase):
    def test_validate_draft_article_rejects_short_forbidden_and_missing_source_detail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chunks_dir = root / "source_cache" / "chunks"
            chunks_dir.mkdir(parents=True)
            (chunks_dir / "chaos-rising.json").write_text(json.dumps([
                {"id": "chaos-rising:0000", "book_slug": "chaos-rising", "text": "David studies forbidden engineering under curfew pressure", "word_count": 7},
                {"id": "chaos-rising:0001", "book_slug": "chaos-rising", "text": "Freemen recruitment depends on competence and trust", "word_count": 7},
            ]), encoding="utf-8")
            draft = {
                "slug": "bad-draft",
                "title": "Bad Draft",
                "description": "Bad",
                "book_slug": "chaos-rising",
                "official_title": "Chaos Rising",
                "official_year": 2082,
                "site_anchor": "https://exodus.orsontbadger.com/#book-1",
                "topic_id": "topic-1",
                "thesis": "A specific thesis about resistance.",
                "source_chunks": ["chaos-rising:0000", "chaos-rising:0001"],
                "concrete_details": ["detail not visible", "another missing", "third missing"],
                "body_html": "<p>Leaving Home — too short.</p>",
            }

            result = validate_draft_article(draft, source_cache_dir=root / "source_cache")

            self.assertFalse(result["ok"])
            joined = "\n".join(result["errors"])
            self.assertIn("800-1200", joined)
            self.assertIn("forbidden visible text", joined)
            self.assertIn("concrete detail missing", joined)

    def test_validate_draft_article_accepts_source_backed_official_metadata_and_word_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chunks_dir = root / "source_cache" / "chunks"
            chunks_dir.mkdir(parents=True)
            (chunks_dir / "chaos-rising.json").write_text(json.dumps([
                {"id": "chaos-rising:0000", "book_slug": "chaos-rising", "text": "curfew pressure technical study Freemen recruitment", "word_count": 6},
                {"id": "chaos-rising:0001", "book_slug": "chaos-rising", "text": "engineering discipline trusted competence rebellion", "word_count": 5},
            ]), encoding="utf-8")
            body = f"<p>Chaos Rising 2082 https://exodus.orsontbadger.com/#book-1 curfew pressure technical study Freemen recruitment {words(810)}</p>"
            draft = {
                "slug": "good-draft",
                "title": "Good Draft",
                "description": "Good",
                "book_slug": "chaos-rising",
                "official_title": "Chaos Rising",
                "official_year": 2082,
                "site_anchor": "https://exodus.orsontbadger.com/#book-1",
                "topic_id": "topic-1",
                "thesis": "Chaos Rising shows resistance forming through disciplined competence.",
                "source_chunks": ["chaos-rising:0000", "chaos-rising:0001"],
                "concrete_details": ["curfew pressure", "technical study", "Freemen recruitment"],
                "body_html": body,
            }

            result = validate_draft_article(draft, source_cache_dir=root / "source_cache")

            self.assertTrue(result["ok"], result)
            self.assertGreaterEqual(result["visible_word_count"], 800)


if __name__ == "__main__":
    unittest.main()
