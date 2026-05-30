import json
import tempfile
import unittest
from pathlib import Path

from scripts.publish_ready import publish_one_ready_draft, validate_homepage_links_and_order


def words(n):
    return " ".join(f"word{i}" for i in range(n))


class PublishReadyTests(unittest.TestCase):
    def test_publish_one_ready_draft_publishes_exactly_one_receipt_and_homepage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ready = root / "drafts" / "ready"
            source_chunks = root / "source_cache" / "chunks"
            ready.mkdir(parents=True)
            source_chunks.mkdir(parents=True)
            (source_chunks / "chaos-rising.json").write_text(json.dumps([
                {"id": "chaos-rising:0000", "book_slug": "chaos-rising", "text": "curfew pressure technical study Freemen recruitment", "word_count": 6},
                {"id": "chaos-rising:0001", "book_slug": "chaos-rising", "text": "engineering discipline trusted competence rebellion", "word_count": 5},
            ]), encoding="utf-8")
            draft = {
                "slug": "chaos-rising-discipline",
                "title": "Discipline Before Revolt",
                "description": "A Chaos Rising field note.",
                "book_slug": "chaos-rising",
                "official_title": "Chaos Rising",
                "official_year": 2082,
                "site_anchor": "https://exodus.orsontbadger.com/#book-1",
                "topic_id": "topic-1",
                "thesis": "Chaos Rising shows resistance forming through disciplined competence.",
                "source_chunks": ["chaos-rising:0000", "chaos-rising:0001"],
                "concrete_details": ["curfew pressure", "technical study", "Freemen recruitment"],
                "body_html": f"<p>Chaos Rising 2082 https://exodus.orsontbadger.com/#book-1 curfew pressure technical study Freemen recruitment {words(810)}</p>",
            }
            (ready / "001.json").write_text(json.dumps(draft, indent=2), encoding="utf-8")

            result = publish_one_ready_draft(root=root)

            self.assertTrue(result["ok"], result)
            self.assertEqual(result["slug"], "chaos-rising-discipline")
            self.assertTrue((root / "articles" / "chaos-rising-discipline.html").exists())
            self.assertTrue((root / "article_meta" / "chaos-rising-discipline.json").exists())
            self.assertFalse((ready / "001.json").exists())
            self.assertIn("chaos-rising-discipline.html", (root / "index.html").read_text(encoding="utf-8"))
            self.assertTrue(validate_homepage_links_and_order(root=root)["ok"])

    def test_homepage_validation_rejects_duplicate_article_titles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            articles = root / "articles"
            articles.mkdir()
            (articles / "one.html").write_text("<h1>Same Title</h1>", encoding="utf-8")
            (articles / "two.html").write_text("<h1>Same Title</h1>", encoding="utf-8")
            (root / "index.html").write_text("<style>.grid{}.article-wrap{}.post-card{}.sticky-cta{}.sales-card{}</style><article class='post-card'><div>Essay 02</div><a href='articles/two.html'>Read</a></article><article class='post-card'><div>Essay 01</div><a href='articles/one.html'>Read</a></article>", encoding="utf-8")

            result = validate_homepage_links_and_order(root=root)

            self.assertFalse(result["ok"])
            self.assertTrue(any("duplicate article title Same Title" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
