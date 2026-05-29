"""Validate source-backed Exodus draft article JSON."""

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

REQUIRED_DRAFT_FIELDS = [
    "slug",
    "title",
    "description",
    "book_slug",
    "official_title",
    "official_year",
    "site_anchor",
    "topic_id",
    "thesis",
    "source_chunks",
    "body_html",
]


def _load_source_chunks(source_cache_dir: str | Path) -> dict[str, dict[str, Any]]:
    chunks_by_id: dict[str, dict[str, Any]] = {}
    chunks_dir = Path(source_cache_dir) / "chunks"
    if not chunks_dir.exists():
        return chunks_by_id
    for path in chunks_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for chunk in data:
            if chunk.get("id"):
                chunks_by_id[str(chunk["id"])] = chunk
    return chunks_by_id


def validate_draft_article(
    draft: dict[str, Any],
    *,
    source_cache_dir: str | Path = DEFAULT_OUTPUT_DIR,
    min_words: int = 800,
    max_words: int = 1200,
) -> dict[str, Any]:
    errors: list[str] = []
    for field in REQUIRED_DRAFT_FIELDS:
        if not draft.get(field):
            errors.append(f"missing {field}")

    body_html = str(draft.get("body_html", ""))
    visible = exodus_common.visible_text_from_html(body_html)
    visible_word_count = exodus_common.visible_word_count(body_html)
    if visible_word_count < min_words or visible_word_count > max_words:
        errors.append(f"visible word count {visible_word_count} outside {min_words}-{max_words}")

    forbidden = exodus_common.find_forbidden_visible_text(body_html)
    if forbidden:
        errors.append(f"forbidden visible text: {', '.join(forbidden)}")

    official_title = str(draft.get("official_title", ""))
    official_year = str(draft.get("official_year", ""))
    site_anchor = str(draft.get("site_anchor", ""))
    if official_title and official_title not in visible:
        errors.append(f"official title missing from visible body: {official_title}")
    if official_year and official_year not in visible:
        errors.append(f"official year missing from visible body: {official_year}")
    if site_anchor and site_anchor not in body_html:
        errors.append(f"CTA anchor missing from body_html: {site_anchor}")

    source_chunks = [str(chunk_id) for chunk_id in draft.get("source_chunks", [])]
    if len(source_chunks) < 2:
        errors.append("draft must cite at least 2 source chunks")
    chunks_by_id = _load_source_chunks(source_cache_dir)
    missing_chunks = [chunk_id for chunk_id in source_chunks if chunk_id not in chunks_by_id]
    if missing_chunks:
        errors.append(f"unknown source chunks: {', '.join(missing_chunks)}")

    if draft.get("book_slug"):
        wrong_book = [chunk_id for chunk_id in source_chunks if chunks_by_id.get(chunk_id, {}).get("book_slug") != draft.get("book_slug")]
        if wrong_book:
            errors.append(f"source chunks from wrong book: {', '.join(wrong_book)}")

    for detail in draft.get("concrete_details", []):
        detail_text = str(detail).strip()
        if detail_text and detail_text.lower() not in visible.lower():
            errors.append(f"concrete detail missing from visible body: {detail_text}")

    return {
        "ok": not errors,
        "errors": errors,
        "visible_word_count": visible_word_count,
        "source_chunks": source_chunks,
        "visible_text": visible,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Exodus draft article JSON.")
    parser.add_argument("draft_json")
    parser.add_argument("--source-cache", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args(list(argv) if argv is not None else None)
    draft = json.loads(Path(args.draft_json).read_text(encoding="utf-8"))
    report = validate_draft_article(draft, source_cache_dir=args.source_cache)
    printable = dict(report)
    printable.pop("visible_text", None)
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
