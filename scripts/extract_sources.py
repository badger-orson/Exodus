"""Extract readable source chunks from Exodus EPUB files.

The extractor intentionally uses only the Python standard library. EPUB files are
ZIP archives; this module reads HTML-family members, converts them to visible
text with :mod:`scripts.exodus_common`, splits the text into stable word chunks,
and writes deterministic JSON cache files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typing import Any, Iterable

from scripts import exodus_common

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "source_cache"
HTML_SUFFIXES = (".xhtml", ".html", ".htm")
DEFAULT_CHUNK_MIN_WORDS = 350
DEFAULT_CHUNK_MAX_WORDS = 700


def normalize_whitespace(text: str) -> str:
    """Collapse all whitespace runs to single spaces and trim edges."""

    return " ".join((text or "").split())


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text or ""))


def _atomic_write_json(path: str | Path, data: Any) -> None:
    """Write JSON to *path* atomically using a sibling temporary file."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=str(destination.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_name, destination)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _is_html_member(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(HTML_SUFFIXES) and not name.endswith("/")


def extract_epub_text_members(epub_path: str | Path) -> list[dict[str, Any]]:
    """Return visible text for each HTML-family member in an EPUB archive.

    Members are processed by sorted archive path for deterministic output. The
    returned dictionaries contain ``source_member``, zero-based ``spine_index``,
    ``text``, and ``word_count``.
    """

    path = Path(epub_path)
    members: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as archive:
        html_names = sorted(name for name in archive.namelist() if _is_html_member(name))
        for spine_index, name in enumerate(html_names):
            raw = archive.read(name)
            markup = raw.decode("utf-8", errors="replace")
            text = normalize_whitespace(exodus_common.visible_text_from_html(markup))
            if not text:
                continue
            members.append(
                {
                    "source_member": name,
                    "spine_index": spine_index,
                    "text": text,
                    "word_count": _word_count(text),
                }
            )
    return members


def split_text_into_chunks(
    text: str,
    *,
    min_words: int = DEFAULT_CHUNK_MIN_WORDS,
    max_words: int = DEFAULT_CHUNK_MAX_WORDS,
) -> list[str]:
    """Split normalized text into stable chunks no larger than ``max_words``.

    The real pipeline defaults to 350-700 word chunks. Tests can pass much
    smaller limits. A short final chunk is merged into the previous chunk when
    possible without violating ``max_words``; otherwise it is kept, because EPUB
    sections can naturally end with short fragments.
    """

    if min_words < 1:
        raise ValueError("min_words must be at least 1")
    if max_words < min_words:
        raise ValueError("max_words must be greater than or equal to min_words")

    words = normalize_whitespace(text).split()
    if not words:
        return []

    chunks: list[list[str]] = []
    for start in range(0, len(words), max_words):
        chunks.append(words[start : start + max_words])

    if len(chunks) > 1 and len(chunks[-1]) < min_words:
        final = chunks[-1]
        previous = chunks[-2]
        if len(previous) + len(final) <= max_words:
            previous.extend(final)
            chunks.pop()

    return [" ".join(chunk) for chunk in chunks]


def chunks_for_book(
    book: dict[str, Any],
    *,
    chunk_min_words: int = DEFAULT_CHUNK_MIN_WORDS,
    chunk_max_words: int = DEFAULT_CHUNK_MAX_WORDS,
) -> list[dict[str, Any]]:
    """Extract source chunks for one metadata book record."""

    book_slug = str(book.get("slug") or exodus_common.slugify_title(str(book["title"])))
    official_title = str(book["title"])
    official_year = int(book["official_year"])
    source_path = str(book["epub"])

    chunks: list[dict[str, Any]] = []
    for member in extract_epub_text_members(source_path):
        for chunk_text in split_text_into_chunks(
            member["text"], min_words=chunk_min_words, max_words=chunk_max_words
        ):
            chunks.append(
                {
                    "id": f"{book_slug}:{len(chunks):04d}",
                    "book_slug": book_slug,
                    "official_title": official_title,
                    "official_year": official_year,
                    "source_path": source_path,
                    "spine_index": member["spine_index"],
                    "text": chunk_text,
                    "word_count": _word_count(chunk_text),
                }
            )
    return chunks


def build_source_cache(
    *,
    metadata_path: str | Path = exodus_common.DEFAULT_METADATA_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    chunk_min_words: int = DEFAULT_CHUNK_MIN_WORDS,
    chunk_max_words: int = DEFAULT_CHUNK_MAX_WORDS,
) -> dict[str, Any]:
    """Build ``source_cache/books.json`` and per-book chunk JSON files."""

    metadata = exodus_common.load_metadata(metadata_path)
    cache_dir = Path(output_dir)
    chunks_dir = cache_dir / "chunks"
    books_index: dict[str, Any] = {"books": []}

    for book in metadata.get("books", []):
        chunks = chunks_for_book(
            book,
            chunk_min_words=chunk_min_words,
            chunk_max_words=chunk_max_words,
        )
        book_slug = str(book["slug"])
        chunk_path = chunks_dir / f"{book_slug}.json"
        _atomic_write_json(chunk_path, chunks)
        books_index["books"].append(
            {
                "book_slug": book_slug,
                "chunk_count": len(chunks),
                "chunks_path": str(chunk_path),
                "official_title": str(book["title"]),
                "official_year": int(book["official_year"]),
                "source_path": str(book.get("epub", "")),
            }
        )

    _atomic_write_json(cache_dir / "books.json", books_index)
    return books_index


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract Exodus EPUBs into source_cache JSON.")
    parser.add_argument("--metadata", default=str(exodus_common.DEFAULT_METADATA_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--chunk-min-words", type=int, default=DEFAULT_CHUNK_MIN_WORDS)
    parser.add_argument("--chunk-max-words", type=int, default=DEFAULT_CHUNK_MAX_WORDS)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    build_source_cache(
        metadata_path=args.metadata,
        output_dir=args.output,
        chunk_min_words=args.chunk_min_words,
        chunk_max_words=args.chunk_max_words,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
