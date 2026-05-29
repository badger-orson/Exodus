import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_sources import validate_source_cache


class ValidateSourcesTests(unittest.TestCase):
    def test_validate_source_cache_requires_each_metadata_book_to_have_chunks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "metadata.json"
            cache = root / "source_cache"
            chunks = cache / "chunks"
            chunks.mkdir(parents=True)
            metadata.write_text(json.dumps({"books": [{"title": "Chaos Rising", "official_year": 2082, "epub": str(root / "book.epub")}]}, indent=2), encoding="utf-8")
            (root / "book.epub").write_text("fake", encoding="utf-8")
            (cache / "books.json").write_text(json.dumps({"books": [{"book_slug": "chaos-rising", "chunk_count": 0, "chunks_path": str(chunks / "chaos-rising.json"), "official_title": "Chaos Rising", "official_year": 2082, "source_path": str(root / "book.epub")}]}, indent=2), encoding="utf-8")
            (chunks / "chaos-rising.json").write_text("[]", encoding="utf-8")

            result = validate_source_cache(metadata_path=metadata, cache_dir=cache)

            self.assertFalse(result["ok"])
            self.assertIn("has no chunks", "\n".join(result["errors"]))

    def test_validate_source_cache_accepts_required_chunk_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "metadata.json"
            cache = root / "source_cache"
            chunks = cache / "chunks"
            chunks.mkdir(parents=True)
            epub = root / "book.epub"
            epub.write_text("fake", encoding="utf-8")
            metadata.write_text(json.dumps({"books": [{"title": "Chaos Rising", "official_year": 2082, "epub": str(epub)}]}, indent=2), encoding="utf-8")
            chunk = {"id": "chaos-rising:0000", "book_slug": "chaos-rising", "official_title": "Chaos Rising", "official_year": 2082, "source_path": str(epub), "spine_index": 0, "text": "one two three four", "word_count": 4}
            (chunks / "chaos-rising.json").write_text(json.dumps([chunk], indent=2), encoding="utf-8")
            (cache / "books.json").write_text(json.dumps({"books": [{"book_slug": "chaos-rising", "chunk_count": 1, "chunks_path": str(chunks / "chaos-rising.json"), "official_title": "Chaos Rising", "official_year": 2082, "source_path": str(epub)}]}, indent=2), encoding="utf-8")

            result = validate_source_cache(metadata_path=metadata, cache_dir=cache)

            self.assertTrue(result["ok"], result)
            self.assertEqual(result["chunk_count"], 1)


if __name__ == "__main__":
    unittest.main()
