import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts import extract_sources


class ExtractSourcesTests(unittest.TestCase):
    def _write_fake_epub(self, path: Path) -> None:
        with zipfile.ZipFile(path, "w") as epub:
            epub.writestr("mimetype", "application/epub+zip")
            epub.writestr(
                "OEBPS/chapter-02.xhtml",
                """
                <html><head>
                  <title>Hidden title</title>
                  <style>.x { display: none; }</style>
                  <script>hidden script words</script>
                </head><body>
                  <h1>Second Chapter</h1>
                  <p>Alpha beta gamma delta.</p>
                  <p>Epsilon    zeta\neta theta.</p>
                </body></html>
                """,
            )
            epub.writestr("OEBPS/ignored.css", "not book text")
            epub.writestr(
                "OEBPS/chapter-01.html",
                """
                <html><body>
                  <p>First chapter has visible words and &amp; entities.</p>
                  <img alt="ignored alt text" src="cover.jpg" />
                </body></html>
                """,
            )
            epub.writestr(
                "OEBPS/appendix.htm",
                "<html><body><p>Appendix final words arrive here.</p></body></html>",
            )

    def test_extract_epub_text_members_reads_only_html_family_and_normalizes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            epub_path = Path(tmpdir) / "fake.epub"
            self._write_fake_epub(epub_path)

            members = extract_sources.extract_epub_text_members(epub_path)

        self.assertEqual(
            [member["source_member"] for member in members],
            ["OEBPS/appendix.htm", "OEBPS/chapter-01.html", "OEBPS/chapter-02.xhtml"],
        )
        self.assertEqual(members[0]["spine_index"], 0)
        combined_text = " ".join(member["text"] for member in members)
        self.assertIn("First chapter has visible words and & entities.", combined_text)
        self.assertIn("Second Chapter Alpha beta gamma delta. Epsilon zeta eta theta.", combined_text)
        self.assertNotIn("hidden script words", combined_text)
        self.assertNotIn("not book text", combined_text)
        self.assertNotIn("ignored alt text", combined_text)

    def test_build_source_cache_writes_books_index_and_chunk_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            epub_path = root / "fake.epub"
            self._write_fake_epub(epub_path)
            metadata_path = root / "exodus_metadata.json"
            metadata_path.write_text(
                json.dumps(
                    {
                        "series": "EXODUS",
                        "books": [
                            {
                                "position": 1,
                                "title": "Chaos Rising",
                                "official_year": 2082,
                                "site_anchor": "https://example.test/#book-1",
                                "epub": str(epub_path),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_dir = root / "source_cache"

            books_index = extract_sources.build_source_cache(
                metadata_path=metadata_path,
                output_dir=output_dir,
                chunk_min_words=4,
                chunk_max_words=6,
            )

            books_json = json.loads((output_dir / "books.json").read_text(encoding="utf-8"))
            chunks_json = json.loads((output_dir / "chunks" / "chaos-rising.json").read_text(encoding="utf-8"))

        self.assertEqual(books_index, books_json)
        self.assertEqual(books_json["books"][0]["book_slug"], "chaos-rising")
        self.assertEqual(books_json["books"][0]["official_title"], "Chaos Rising")
        self.assertEqual(books_json["books"][0]["official_year"], 2082)
        self.assertGreaterEqual(books_json["books"][0]["chunk_count"], 3)
        self.assertEqual(len(chunks_json), books_json["books"][0]["chunk_count"])

        first_chunk = chunks_json[0]
        self.assertEqual(first_chunk["id"], "chaos-rising:0000")
        self.assertEqual(first_chunk["book_slug"], "chaos-rising")
        self.assertEqual(first_chunk["official_title"], "Chaos Rising")
        self.assertEqual(first_chunk["official_year"], 2082)
        self.assertEqual(first_chunk["source_path"], str(epub_path))
        self.assertEqual(first_chunk["spine_index"], 0)
        self.assertLessEqual(first_chunk["word_count"], 6)
        self.assertEqual(first_chunk["word_count"], len(first_chunk["text"].split()))
        self.assertTrue(all(set(chunk) >= {"id", "book_slug", "official_title", "official_year", "source_path", "spine_index", "text", "word_count"} for chunk in chunks_json))


if __name__ == "__main__":
    unittest.main()
