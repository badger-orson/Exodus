import json
import tempfile
import unittest
from pathlib import Path

from scripts import exodus_common


class ExodusCommonTests(unittest.TestCase):
    def test_visible_text_strips_html_script_style_and_collapses_whitespace(self):
        html = """
        <html>
          <head>
            <style>.hidden { color: red; }</style>
            <script>window.bad = 'not visible';</script>
            <title>Ignored title</title>
          </head>
          <body>
            <h1>Field Note</h1>
            <p>David &amp; Mara<br>cross the yard.</p>
          </body>
        </html>
        """

        self.assertEqual(
            exodus_common.visible_text_from_html(html),
            "Field Note David & Mara cross the yard.",
        )

    def test_visible_word_count_counts_only_visible_words(self):
        html = """
        <style>four five six</style>
        <script>seven eight</script>
        <p>One two, three.</p><p>Chaos Rising 2082.</p>
        """

        self.assertEqual(exodus_common.visible_word_count(html), 6)

    def test_find_forbidden_visible_text_detects_configured_terms_and_emdash(self):
        html = """
        <style>2032 Leaving Home — hidden here</style>
        <p>Clean visible text mentions Reprisal and a bad dash — here.</p>
        """

        self.assertEqual(
            exodus_common.find_forbidden_visible_text(html),
            ["Reprisal", "—"],
        )

    def test_slugify_title_normalizes_official_titles(self):
        cases = {
            "Chaos Rising": "chaos-rising",
            "MoonBound": "moonbound",
            "BioRift": "biorift",
            "SandRats": "sandrats",
            "  The Ark's End!  ": "the-ark-s-end",
        }

        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertEqual(exodus_common.slugify_title(title), expected)

    def test_load_metadata_exposes_books_by_official_title_and_slug(self):
        metadata = {
            "series": "EXODUS",
            "books": [
                {
                    "position": 1,
                    "title": "Chaos Rising",
                    "official_year": 2082,
                    "site_anchor": "https://example.test/#book-1",
                },
                {
                    "position": 3,
                    "title": "MoonBound",
                    "official_year": 2087,
                    "site_anchor": "https://example.test/#book-3",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            metadata_path = Path(tmpdir) / "metadata.json"
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

            loaded = exodus_common.load_metadata(metadata_path)

        self.assertEqual(loaded["series"], "EXODUS")
        self.assertEqual(loaded["books_by_title"]["Chaos Rising"]["slug"], "chaos-rising")
        self.assertEqual(loaded["books_by_slug"]["moonbound"]["title"], "MoonBound")
        self.assertEqual(loaded["books_by_slug"]["chaos-rising"]["official_year"], 2082)


if __name__ == "__main__":
    unittest.main()
