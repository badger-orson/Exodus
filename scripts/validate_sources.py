"""Validate EPUB-derived Exodus source caches."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typing import Any, Iterable

from scripts import exodus_common
from scripts.extract_sources import DEFAULT_OUTPUT_DIR

REQUIRED_CHUNK_FIELDS = {
    "id",
    "book_slug",
    "official_title",
    "official_year",
    "source_path",
    "spine_index",
    "text",
    "word_count",
}


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_source_cache(
    *,
    metadata_path: str | Path = exodus_common.DEFAULT_METADATA_PATH,
    cache_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    """Return a validation report for ``source_cache``.

    The cache is valid only when every official metadata book has a book index
    entry, the referenced chunk file exists, and every chunk has required fields.
    """

    errors: list[str] = []
    cache = Path(cache_dir)
    books_json = cache / "books.json"
    if not books_json.exists():
        return {"ok": False, "errors": [f"missing {books_json}"], "book_count": 0, "chunk_count": 0}

    metadata = exodus_common.load_metadata(metadata_path)
    index = _load_json(books_json)
    by_slug = {str(book.get("book_slug")): book for book in index.get("books", [])}
    total_chunks = 0

    for book in metadata.get("books", []):
        slug = str(book["slug"])
        entry = by_slug.get(slug)
        if not entry:
            errors.append(f"{slug} missing from books.json")
            continue
        source_path = Path(str(book.get("epub", "")))
        if not source_path.exists():
            errors.append(f"{slug} metadata epub does not exist: {source_path}")
        if int(entry.get("chunk_count", 0)) <= 0:
            errors.append(f"{slug} has no chunks")
        chunks_path = Path(str(entry.get("chunks_path", cache / "chunks" / f"{slug}.json")))
        if not chunks_path.exists():
            errors.append(f"{slug} missing chunk file: {chunks_path}")
            continue
        chunks = _load_json(chunks_path)
        if not isinstance(chunks, list):
            errors.append(f"{slug} chunk file is not a list")
            continue
        if len(chunks) != int(entry.get("chunk_count", len(chunks))):
            errors.append(f"{slug} chunk_count does not match chunk file length")
        for chunk in chunks:
            missing = sorted(REQUIRED_CHUNK_FIELDS - set(chunk))
            if missing:
                errors.append(f"{slug} chunk missing fields: {', '.join(missing)}")
                continue
            if chunk["book_slug"] != slug:
                errors.append(f"{chunk.get('id')} book_slug mismatch")
            if not str(chunk.get("text", "")).strip():
                errors.append(f"{chunk.get('id')} empty text")
            if int(chunk.get("word_count", 0)) <= 0:
                errors.append(f"{chunk.get('id')} invalid word_count")
        total_chunks += len(chunks)

    return {"ok": not errors, "errors": errors, "book_count": len(metadata.get("books", [])), "chunk_count": total_chunks}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Exodus source_cache JSON.")
    parser.add_argument("--metadata", default=str(exodus_common.DEFAULT_METADATA_PATH))
    parser.add_argument("--cache", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = validate_source_cache(metadata_path=args.metadata, cache_dir=args.cache)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
