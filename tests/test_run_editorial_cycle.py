import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_editorial_cycle import run_editorial_cycle


class RunEditorialCycleTests(unittest.TestCase):
    def test_run_editorial_cycle_selects_only_publishable_source_chunks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chunks = root / "source_cache" / "chunks"
            chunks.mkdir(parents=True)
            (root / "source_cache" / "books.json").write_text(json.dumps({"books": [{"book_slug": "chaos-rising", "chunk_count": 3, "chunks_path": str(chunks / "chaos-rising.json"), "official_title": "Chaos Rising", "official_year": 2082, "source_path": "book.epub"}]}), encoding="utf-8")
            (chunks / "chaos-rising.json").write_text(json.dumps([
                {"id": "chaos-rising:0000", "book_slug": "chaos-rising", "official_title": "Chaos Rising", "official_year": 2082, "text": "EXODUS Leaving Home old front matter", "word_count": 5},
                {"id": "chaos-rising:0001", "book_slug": "chaos-rising", "official_title": "Chaos Rising", "official_year": 2082, "text": "too short clean", "word_count": 3},
                {"id": "chaos-rising:0013", "book_slug": "chaos-rising", "official_title": "Chaos Rising", "official_year": 2082, "text": "compliance patrol unauthorized school locker without a lock " * 30, "word_count": 210},
            ]), encoding="utf-8")

            result = run_editorial_cycle(root=root, allow_extract=False)

            ids = [chunk["id"] for chunk in result["selected_source_chunks"]]
            self.assertEqual(ids, ["chaos-rising:0013"])

    def test_run_editorial_cycle_reports_needs_agent_draft_when_no_ready_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source_cache" / "chunks").mkdir(parents=True)
            (root / "source_cache" / "books.json").write_text(json.dumps({"books": [{"book_slug": "chaos-rising", "chunk_count": 1, "chunks_path": str(root / "source_cache" / "chunks" / "chaos-rising.json"), "official_title": "Chaos Rising", "official_year": 2082, "source_path": "book.epub"}]}), encoding="utf-8")
            (root / "source_cache" / "chunks" / "chaos-rising.json").write_text(json.dumps([{"id": "chaos-rising:0000", "book_slug": "chaos-rising", "official_title": "Chaos Rising", "official_year": 2082, "text": "curfew pressure technical study Freemen recruitment", "word_count": 6}]), encoding="utf-8")

            result = run_editorial_cycle(root=root, allow_extract=False)

            self.assertFalse(result["ok"])
            self.assertEqual(result["status"], "NEEDS_AGENT_DRAFT")
            self.assertIn("draft_schema", result)
            self.assertIn("selected_source_chunks", result)


if __name__ == "__main__":
    unittest.main()
