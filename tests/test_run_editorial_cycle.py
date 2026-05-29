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

    def test_run_editorial_cycle_reports_source_shortage_when_no_publishable_pair_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source_cache" / "chunks").mkdir(parents=True)
            (root / "source_cache" / "books.json").write_text(json.dumps({"books": [{"book_slug": "chaos-rising", "chunk_count": 1, "chunks_path": str(root / "source_cache" / "chunks" / "chaos-rising.json"), "official_title": "Chaos Rising", "official_year": 2082, "source_path": "book.epub"}]}), encoding="utf-8")
            (root / "source_cache" / "chunks" / "chaos-rising.json").write_text(json.dumps([{"id": "chaos-rising:0000", "book_slug": "chaos-rising", "official_title": "Chaos Rising", "official_year": 2082, "text": "curfew pressure technical study Freemen recruitment", "word_count": 6}]), encoding="utf-8")

            result = run_editorial_cycle(root=root, allow_extract=False)

            self.assertFalse(result["ok"])
            self.assertEqual(result["status"], "NEEDS_SOURCE_CHUNKS")
            self.assertIn("draft_schema", result)
            self.assertIn("selected_source_chunks", result)

    def test_run_editorial_cycle_generates_and_publishes_without_agent_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chunks = root / "source_cache" / "chunks"
            chunks.mkdir(parents=True)
            (root / "source_cache" / "books.json").write_text(json.dumps({"books": [{"book_slug": "biorift", "chunk_count": 2, "chunks_path": str(chunks / "biorift.json"), "official_title": "BioRift", "official_year": 2898, "source_path": "book.epub"}]}), encoding="utf-8")
            source_text = "Miah Elias Sergeant Anders Earthers Dome 3 Ark Police Portar tourniquet lift shaft security troops ag-workers reception counter optical nerves survival pressure " * 20
            (chunks / "biorift.json").write_text(json.dumps([
                {"id": "biorift:0006", "book_slug": "biorift", "official_title": "BioRift", "official_year": 2898, "text": source_text, "word_count": 240},
                {"id": "biorift:0007", "book_slug": "biorift", "official_title": "BioRift", "official_year": 2898, "text": source_text, "word_count": 240},
            ]), encoding="utf-8")

            result = run_editorial_cycle(root=root, allow_extract=False)

            self.assertTrue(result["ok"], result)
            self.assertEqual(result["status"], "PUBLISHED")
            self.assertTrue((root / "articles" / "biorift-biorift-0006-field-note.html").exists())
            self.assertTrue((root / "article_meta" / "biorift-biorift-0006-field-note.json").exists())
            self.assertFalse(list((root / "drafts" / "ready").glob("*.json")))


if __name__ == "__main__":
    unittest.main()
