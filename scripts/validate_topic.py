"""Validate source-backed Exodus topic candidates and used-topic ledger."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_TOPICS_DIR = Path(__file__).resolve().parents[1] / "topics"
DEFAULT_USED_TOPICS_PATH = DEFAULT_TOPICS_DIR / "used_topics.json"
GENERIC_THESES = {
    "this book has themes.",
    "this is a theme.",
    "this article is about survival.",
    "the story is interesting.",
}


def _atomic_write_json(path: str | Path, data: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=str(destination.parent))
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


def _load_ledger(path: str | Path | None = DEFAULT_USED_TOPICS_PATH) -> dict[str, Any]:
    if path is None:
        return {"used_topics": []}
    ledger_path = Path(path)
    if not ledger_path.exists():
        return {"used_topics": []}
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"used_topics": data}
    return data


def load_used_topic_ids(path: str | Path | None = DEFAULT_USED_TOPICS_PATH) -> set[str]:
    ledger = _load_ledger(path)
    return {str(item.get("id")) for item in ledger.get("used_topics", []) if item.get("id")}


def validate_topic_candidate(
    topic: dict[str, Any],
    *,
    used_topics_path: str | Path | None = DEFAULT_USED_TOPICS_PATH,
    available_chunk_ids: set[str] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    required = ["id", "book_slug", "official_title", "official_year", "topic", "thesis", "source_chunks", "concrete_details", "why_readers_care"]
    for field in required:
        if not topic.get(field):
            errors.append(f"missing {field}")

    source_chunks = [str(chunk_id) for chunk_id in topic.get("source_chunks", [])]
    if len(source_chunks) < 2:
        errors.append("topic must cite at least 2 source chunks")
    if len([d for d in topic.get("concrete_details", []) if str(d).strip()]) < 3:
        errors.append("topic must include at least 3 concrete details")

    thesis = str(topic.get("thesis", "")).strip()
    if len(thesis.split()) < 8 or thesis.lower() in GENERIC_THESES:
        errors.append("topic must have a non-generic thesis")

    topic_id = str(topic.get("id", ""))
    if topic_id and topic_id in load_used_topic_ids(used_topics_path):
        errors.append(f"topic already used: {topic_id}")

    if available_chunk_ids is not None:
        missing_chunks = sorted(set(source_chunks) - set(available_chunk_ids))
        if missing_chunks:
            errors.append(f"unknown source chunks: {', '.join(missing_chunks)}")

    return {"ok": not errors, "errors": errors, "topic_id": topic_id}


def mark_topic_used(topic: dict[str, Any], path: str | Path = DEFAULT_USED_TOPICS_PATH) -> None:
    ledger = _load_ledger(path)
    used = ledger.setdefault("used_topics", [])
    topic_id = str(topic.get("id") or topic.get("topic_id"))
    if not topic_id or topic_id == "None":
        raise KeyError("id")
    if topic_id not in {str(item.get("id")) for item in used}:
        used.append(
            {
                "id": topic_id,
                "book_slug": topic.get("book_slug"),
                "topic": topic.get("topic"),
                "thesis": topic.get("thesis"),
                "used_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            }
        )
    _atomic_write_json(path, ledger)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a topic candidate JSON file.")
    parser.add_argument("topic_json")
    parser.add_argument("--used-topics", default=str(DEFAULT_USED_TOPICS_PATH))
    args = parser.parse_args(list(argv) if argv is not None else None)
    topic = json.loads(Path(args.topic_json).read_text(encoding="utf-8"))
    report = validate_topic_candidate(topic, used_topics_path=args.used_topics)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
