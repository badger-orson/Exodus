import json
import tempfile
import unittest
from pathlib import Path

from scripts.publish_ready import publish_one_ready_draft, validate_homepage_links_and_order, near_duplicate_article_bodies


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

    def test_homepage_validation_rejects_duplicate_article_bodies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            articles = root / "articles"
            articles.mkdir()
            body = '<div class="article-body"><p>Same body text repeated across two article files.</p></div><section class="sales-card"></section>'
            (articles / "one.html").write_text(f"<h1>Title One</h1>{body}", encoding="utf-8")
            (articles / "two.html").write_text(f"<h1>Title Two</h1>{body}", encoding="utf-8")
            (root / "index.html").write_text("<style>.grid{}.article-wrap{}.post-card{}.sticky-cta{}.sales-card{}</style><article class='post-card'><div>Essay 02</div><a href='articles/two.html'>Read</a></article><article class='post-card'><div>Essay 01</div><a href='articles/one.html'>Read</a></article>", encoding="utf-8")

            result = validate_homepage_links_and_order(root=root)

            self.assertFalse(result["ok"])
            self.assertTrue(any("duplicate article body" in error for error in result["errors"]))

    def test_homepage_validation_rejects_near_duplicate_article_bodies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            articles = root / "articles"
            articles.mkdir()
            repeated = " ".join(f"survival pressure systems breaking competence corridor danger token{i}" for i in range(220))
            changed = repeated.replace("token40", "checkpoint40").replace("token120", "checkpoint120")
            body_one = f'<div class="article-body"><p>{repeated}</p></div><section class="sales-card"></section>'
            body_two = f'<div class="article-body"><p>{changed}</p></div><section class="sales-card"></section>'
            (articles / "one.html").write_text(f"<h1>Title One</h1>{body_one}", encoding="utf-8")
            (articles / "two.html").write_text(f"<h1>Title Two</h1>{body_two}", encoding="utf-8")
            (root / "index.html").write_text("<style>.grid{}.article-wrap{}.post-card{}.sticky-cta{}.sales-card{}</style><article class='post-card'><div>Essay 02</div><a href='articles/two.html'>Read</a></article><article class='post-card'><div>Essay 01</div><a href='articles/one.html'>Read</a></article>", encoding="utf-8")

            result = validate_homepage_links_and_order(root=root)

            self.assertFalse(result["ok"])
            self.assertTrue(any("near-duplicate article body" in error for error in result["errors"]))
            self.assertTrue(near_duplicate_article_bodies(root))

    def test_publish_one_ready_draft_rejects_duplicate_article_body_with_new_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ready = root / "drafts" / "ready"
            source_chunks = root / "source_cache" / "chunks"
            articles = root / "articles"
            ready.mkdir(parents=True)
            source_chunks.mkdir(parents=True)
            articles.mkdir()
            body_html = f"<p>Chaos Rising 2082 https://exodus.orsontbadger.com/#book-1 curfew pressure technical study Freemen recruitment {words(810)}</p>"
            (articles / "old.html").write_text(f'<h1>Old Title</h1><div class="article-body">{body_html}</div><section class="sales-card"></section>', encoding="utf-8")
            (source_chunks / "chaos-rising.json").write_text(json.dumps([
                {"id": "chaos-rising:0000", "book_slug": "chaos-rising", "text": "curfew pressure technical study Freemen recruitment", "word_count": 6},
                {"id": "chaos-rising:0001", "book_slug": "chaos-rising", "text": "engineering discipline trusted competence rebellion", "word_count": 5},
            ]), encoding="utf-8")
            draft = {
                "slug": "new-title-same-body",
                "title": "New Title Same Body",
                "description": "A Chaos Rising essay.",
                "book_slug": "chaos-rising",
                "official_title": "Chaos Rising",
                "official_year": 2082,
                "site_anchor": "https://exodus.orsontbadger.com/#book-1",
                "topic_id": "topic-dup-body",
                "thesis": "Chaos Rising shows resistance forming through disciplined competence.",
                "source_chunks": ["chaos-rising:0000", "chaos-rising:0001"],
                "concrete_details": ["curfew pressure", "technical study", "Freemen recruitment"],
                "body_html": body_html,
            }
            (ready / "001.json").write_text(json.dumps(draft, indent=2), encoding="utf-8")

            result = publish_one_ready_draft(root=root)

            self.assertFalse(result["ok"])
            self.assertEqual(result["status"], "DUPLICATE_BODY")
    def test_publish_one_ready_draft_rejects_near_duplicate_article_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ready = root / "drafts" / "ready"
            source_chunks = root / "source_cache" / "chunks"
            articles = root / "articles"
            ready.mkdir(parents=True)
            source_chunks.mkdir(parents=True)
            articles.mkdir()
            repeated = " ".join(f"Chaos Rising 2082 curfew pressure technical study Freemen recruitment survival systems token{i}" for i in range(220))
            old_body = f"<p>{repeated}</p>"
            draft_body = f"<p>{repeated.replace('token40', 'machinery40').replace('token120', 'machinery120')} https://exodus.orsontbadger.com/#book-1</p>"
            (articles / "old.html").write_text(f'<h1>Old Title</h1><div class="article-body">{old_body}</div><section class="sales-card"></section>', encoding="utf-8")
            (source_chunks / "chaos-rising.json").write_text(json.dumps([
                {"id": "chaos-rising:0000", "book_slug": "chaos-rising", "text": "curfew pressure technical study Freemen recruitment", "word_count": 6},
                {"id": "chaos-rising:0001", "book_slug": "chaos-rising", "text": "engineering discipline trusted competence rebellion", "word_count": 5},
            ]), encoding="utf-8")
            draft = {
                "slug": "new-title-near-body",
                "title": "New Title Near Body",
                "description": "A Chaos Rising essay.",
                "book_slug": "chaos-rising",
                "official_title": "Chaos Rising",
                "official_year": 2082,
                "site_anchor": "https://exodus.orsontbadger.com/#book-1",
                "topic_id": "topic-near-body",
                "thesis": "Chaos Rising shows resistance forming through disciplined competence.",
                "source_chunks": ["chaos-rising:0000", "chaos-rising:0001"],
                "concrete_details": ["curfew pressure", "technical study", "Freemen recruitment"],
                "body_html": draft_body,
            }
            (ready / "001.json").write_text(json.dumps(draft, indent=2), encoding="utf-8")

            result = publish_one_ready_draft(root=root)

            self.assertFalse(result["ok"])
            self.assertEqual(result["status"], "NEAR_DUPLICATE_BODY")


if __name__ == "__main__":
    unittest.main()
