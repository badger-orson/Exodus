import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_editorial_cycle import run_editorial_cycle


class PickLastRng:
    def choice(self, values):
        return list(values)[-1]


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
            self.assertTrue((root / "articles" / f"{result['slug']}.html").exists())
            self.assertTrue((root / "article_meta" / f"{result['slug']}.json").exists())
            self.assertFalse(list((root / "drafts" / "ready").glob("*.json")))

    def test_run_editorial_cycle_does_not_repeat_existing_article_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chunks = root / "source_cache" / "chunks"
            chunks.mkdir(parents=True)
            (root / "articles").mkdir()
            (root / "articles" / "old.html").write_text("<h1>The Future Does Not Save Us. It Gives the Monsters Better Tools</h1>", encoding="utf-8")
            (root / "source_cache" / "books.json").write_text(json.dumps({"books": [{"book_slug": "biorift", "chunk_count": 2, "chunks_path": str(chunks / "biorift.json"), "official_title": "BioRift", "official_year": 2898, "source_path": "book.epub"}]}), encoding="utf-8")
            source_text = "Miah Elias Sergeant Anders Earthers Dome 3 Ark Police Portar tourniquet lift shaft security troops ag-workers reception counter optical nerves survival pressure " * 20
            (chunks / "biorift.json").write_text(json.dumps([
                {"id": "biorift:0006", "book_slug": "biorift", "official_title": "BioRift", "official_year": 2898, "text": source_text, "word_count": 240},
                {"id": "biorift:0007", "book_slug": "biorift", "official_title": "BioRift", "official_year": 2898, "text": source_text, "word_count": 240},
            ]), encoding="utf-8")

            result = run_editorial_cycle(root=root, allow_extract=False)

            self.assertTrue(result["ok"], result)
            self.assertNotEqual(result["title"], "The Future Does Not Save Us. It Gives the Monsters Better Tools")

    def test_run_editorial_cycle_chooses_random_book_and_random_part(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chunks = root / "source_cache" / "chunks"
            chunks.mkdir(parents=True)
            (root / "source_cache" / "books.json").write_text(json.dumps({"books": [
                {"book_slug": "chaos-rising", "chunk_count": 2, "chunks_path": str(chunks / "chaos-rising.json"), "official_title": "Chaos Rising", "official_year": 2082, "source_path": "chaos.epub"},
                {"book_slug": "sandrats", "chunk_count": 3, "chunks_path": str(chunks / "sandrats.json"), "official_title": "SandRats", "official_year": 2898, "source_path": "sand.epub"},
            ]}), encoding="utf-8")
            (chunks / "chaos-rising.json").write_text(json.dumps([
                {"id": "chaos-rising:0010", "book_slug": "chaos-rising", "official_title": "Chaos Rising", "official_year": 2082, "text": "curfew lesson hidden Freemen corridor pressure " * 40, "word_count": 240},
                {"id": "chaos-rising:0011", "book_slug": "chaos-rising", "official_title": "Chaos Rising", "official_year": 2082, "text": "underground lesson patrol family risk memory " * 40, "word_count": 240},
            ]), encoding="utf-8")
            (chunks / "sandrats.json").write_text(json.dumps([
                {"id": "sandrats:0020", "book_slug": "sandrats", "official_title": "SandRats", "official_year": 2898, "text": "desert water shelter scouts pressure survival " * 40, "word_count": 240},
                {"id": "sandrats:0021", "book_slug": "sandrats", "official_title": "SandRats", "official_year": 2898, "text": "camp dust ration convoy thirst warning " * 40, "word_count": 240},
                {"id": "sandrats:0022", "book_slug": "sandrats", "official_title": "SandRats", "official_year": 2898, "text": "frontier teeth heat repair maps dunes " * 40, "word_count": 240},
            ]), encoding="utf-8")

            result = run_editorial_cycle(root=root, allow_extract=False, rng=PickLastRng())

            self.assertTrue(result["ok"], result)
            self.assertEqual(result["slug"], "sandrats-sandrats-0022-article")
            self.assertEqual(result["source_chunks"][0], "sandrats:0022")

    def test_generated_article_body_uses_randomly_selected_source_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chunks = root / "source_cache" / "chunks"
            chunks.mkdir(parents=True)
            (root / "source_cache" / "books.json").write_text(json.dumps({"books": [{"book_slug": "biorift", "chunk_count": 2, "chunks_path": str(chunks / "biorift.json"), "official_title": "BioRift", "official_year": 2898, "source_path": "book.epub"}]}), encoding="utf-8")
            first = "Miah studies the reception counter while the optical nerves keep reporting the wrong threat. " * 20
            second = "Elias watches Dome 3 security troops turn the lift shaft into a checkpoint for frightened workers. " * 20
            (chunks / "biorift.json").write_text(json.dumps([
                {"id": "biorift:0040", "book_slug": "biorift", "official_title": "BioRift", "official_year": 2898, "text": first, "word_count": 220},
                {"id": "biorift:0041", "book_slug": "biorift", "official_title": "BioRift", "official_year": 2898, "text": second, "word_count": 220},
            ]), encoding="utf-8")

            result = run_editorial_cycle(root=root, allow_extract=False)

            self.assertTrue(result["ok"], result)
            article = (root / "articles" / f"{result['slug']}.html").read_text(encoding="utf-8")
            self.assertIn("reception counter", article)
            self.assertIn("lift shaft", article)


if __name__ == "__main__":
    unittest.main()
