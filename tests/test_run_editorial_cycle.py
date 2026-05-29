import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_editorial_cycle import run_editorial_cycle


class RunEditorialCycleTests(unittest.TestCase):
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
