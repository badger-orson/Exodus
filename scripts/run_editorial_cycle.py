"""Top-level deterministic Exodus V2 editorial cycle entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typing import Any, Iterable

from scripts.extract_sources import build_source_cache
from scripts.publish_ready import publish_one_ready_draft
from scripts.validate_sources import validate_source_cache

DRAFT_SCHEMA = {
    "slug": "lowercase-dash-slug",
    "title": "human title",
    "description": "SEO/social description",
    "book_slug": "chaos-rising",
    "official_title": "Chaos Rising",
    "official_year": 2082,
    "site_anchor": "https://exodus.orsontbadger.com/#book-1",
    "topic_id": "source-backed-topic-id",
    "topic": "topic label",
    "thesis": "specific non-generic thesis",
    "source_chunks": ["chaos-rising:0000", "chaos-rising:0001"],
    "concrete_details": ["detail one", "detail two", "detail three"],
    "body_html": "<p>800-1200 visible words with CTA anchor.</p>",
}


def _select_context(root: Path) -> dict[str, Any]:
    chunks_dir = root / "source_cache" / "chunks"
    selected: list[dict[str, Any]] = []
    for chunk_file in sorted(chunks_dir.glob("*.json")):
        chunks = json.loads(chunk_file.read_text(encoding="utf-8"))
        for chunk in chunks:
            selected.append(
                {
                    "id": chunk.get("id"),
                    "book_slug": chunk.get("book_slug"),
                    "official_title": chunk.get("official_title"),
                    "official_year": chunk.get("official_year"),
                    "text_excerpt": str(chunk.get("text", ""))[:900],
                    "word_count": chunk.get("word_count"),
                }
            )
            if len(selected) >= 3:
                return {"selected_source_chunks": selected, "draft_schema": DRAFT_SCHEMA}
    return {"selected_source_chunks": selected, "draft_schema": DRAFT_SCHEMA}


def run_editorial_cycle(*, root: str | Path = ".", allow_extract: bool = True) -> dict[str, Any]:
    root_path = Path(root)
    ready = sorted((root_path / "drafts" / "ready").glob("*.json")) if (root_path / "drafts" / "ready").exists() else []
    if ready:
        return publish_one_ready_draft(root=root_path)

    metadata_path = root_path / "exodus_metadata.json"
    if metadata_path.exists():
        cache_report = validate_source_cache(metadata_path=metadata_path, cache_dir=root_path / "source_cache")
        if not cache_report["ok"] and allow_extract:
            build_source_cache(metadata_path=metadata_path, output_dir=root_path / "source_cache")
            cache_report = validate_source_cache(metadata_path=metadata_path, cache_dir=root_path / "source_cache")
        if not cache_report["ok"]:
            return {"ok": False, "status": "SOURCE_CACHE_INVALID", "errors": cache_report["errors"]}
    elif not (root_path / "source_cache" / "books.json").exists():
        return {"ok": False, "status": "SOURCE_CACHE_INVALID", "errors": ["missing exodus_metadata.json and source_cache/books.json"]}

    context = _select_context(root_path)
    return {
        "ok": False,
        "status": "NEEDS_AGENT_DRAFT",
        "message": "Create one draft JSON in drafts/ready using the schema and selected source chunks, then rerun scripts/run_editorial_cycle.py.",
        **context,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one Exodus V2 editorial cycle.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--no-extract", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = run_editorial_cycle(root=args.root, allow_extract=not args.no_extract)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 2 if result.get("status") == "NEEDS_AGENT_DRAFT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
