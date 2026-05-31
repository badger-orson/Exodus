"""Publish one validated V2 ready draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typing import Any, Iterable

from scripts.exodus_common import visible_word_count
from scripts.render_article import render_article_file
from scripts.validate_article import validate_draft_article
from scripts.validate_topic import mark_topic_used

REQUIRED_CSS_SELECTORS = [".grid", ".article-wrap", ".post-card", ".sticky-cta", ".sales-card"]


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


def _first_ready_draft(ready_dir: Path) -> Path | None:
    drafts = sorted(ready_dir.glob("*.json"))
    return drafts[0] if drafts else None


def _run_generate(root: Path) -> None:
    """Regenerate the homepage from the target root.

    Production roots use their local generate.py. Tests and minimal fixtures may not
    have one, so fall back to a small compatible renderer that enforces the same
    link/order/selector contract.
    """

    generate_path = root / "generate.py"
    if not generate_path.exists():
        _fallback_generate_homepage(root)
        return

    import importlib.util

    spec = importlib.util.spec_from_file_location("exodus_generate_runtime", generate_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import generate.py")
    module = importlib.util.module_from_spec(spec)
    cwd = Path.cwd()
    try:
        os.chdir(root)
        spec.loader.exec_module(module)
        module.generate_homepage()
    finally:
        os.chdir(cwd)


def _fallback_generate_homepage(root: Path) -> None:
    articles_dir = root / "articles"
    article_files = sorted(articles_dir.glob("*.html"), key=lambda path: path.stat().st_mtime, reverse=True)
    total = len(article_files)
    cards = []
    for index, article in enumerate(article_files, 1):
        note = total - index + 1
        text = article.read_text(encoding="utf-8")
        title_match = re.search(r"<h1>(.*?)</h1>", text, re.S)
        title = title_match.group(1) if title_match else article.stem.replace("-", " ").title()
        cards.append(f"<article class='post-card'><div><div class='post-meta'>Essay {note:02d} · Exodus Books</div><h3>{title}</h3><p>A sharp path into the Exodus series.</p></div><a class='read-more' href='articles/{article.name}'>Read essay</a></article>")
    html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>.grid{}.article-wrap{}.post-card{}.sticky-cta{}.sales-card{}</style></head><body><div class='grid'>" + "".join(cards) + "</div></body></html>"
    (root / "index.html").write_text(html, encoding="utf-8")


def create_receipt(draft: dict[str, Any], visible_word_count: int) -> dict[str, Any]:
    return {
        "slug": draft["slug"],
        "published_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "book_slug": draft["book_slug"],
        "official_title": draft["official_title"],
        "official_year": draft["official_year"],
        "topic_id": draft["topic_id"],
        "thesis": draft["thesis"],
        "source_chunks": list(draft.get("source_chunks", [])),
        "visible_word_count": visible_word_count,
        "commit": "",
    }




def _strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def _normalize_visible_text(value: str) -> str:
    visible = _strip_tags(value).lower()
    return re.sub(r"[^a-z0-9]+", " ", visible).strip()


def _article_body_html(article_html: str) -> str:
    match = re.search(r'<div class="article-body">(.*?)<section class="sales-card">', article_html, re.S | re.I)
    return match.group(1) if match else article_html


def _body_fingerprint(value: str) -> str:
    normalized = _normalize_visible_text(value)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _word_shingles(value: str, *, size: int = 5) -> set[tuple[str, ...]]:
    words = [word for word in re.findall(r"[a-z0-9]+", _normalize_visible_text(value)) if len(word) > 3]
    if len(words) < size:
        return set()
    return set(zip(*(words[index:] for index in range(size))))


def _jaccard(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def existing_article_body_shingles(root: str | Path = ".") -> dict[str, set[tuple[str, ...]]]:
    root_path = Path(root)
    shingles: dict[str, set[tuple[str, ...]]] = {}
    for article in (root_path / "articles").glob("*.html"):
        text = article.read_text(encoding="utf-8", errors="ignore")
        shingles[article.name] = _word_shingles(_article_body_html(text))
    return shingles


def near_duplicate_article_bodies(root: str | Path = ".", *, threshold: float = 0.72) -> list[tuple[float, str, str]]:
    article_shingles = existing_article_body_shingles(root)
    names = sorted(article_shingles)
    duplicates: list[tuple[float, str, str]] = []
    for left_index, left_name in enumerate(names):
        for right_name in names[left_index + 1 :]:
            score = _jaccard(article_shingles[left_name], article_shingles[right_name])
            if score >= threshold:
                duplicates.append((score, left_name, right_name))
    return duplicates


def existing_article_titles(root: str | Path = ".") -> dict[str, list[str]]:
    root_path = Path(root)
    titles: dict[str, list[str]] = {}
    for article in (root_path / "articles").glob("*.html"):
        text = article.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
        title = _strip_tags(match.group(1)) if match else article.stem.replace("-", " ").title()
        titles.setdefault(title, []).append(article.name)
    return titles


def existing_article_body_fingerprints(root: str | Path = ".") -> dict[str, list[str]]:
    root_path = Path(root)
    fingerprints: dict[str, list[str]] = {}
    for article in (root_path / "articles").glob("*.html"):
        text = article.read_text(encoding="utf-8", errors="ignore")
        fingerprint = _body_fingerprint(_article_body_html(text))
        fingerprints.setdefault(fingerprint, []).append(article.name)
    return fingerprints

def validate_homepage_links_and_order(*, root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    index = root_path / "index.html"
    errors: list[str] = []
    if not index.exists():
        return {"ok": False, "errors": ["missing index.html"]}
    html = index.read_text(encoding="utf-8")
    for selector in REQUIRED_CSS_SELECTORS:
        if selector not in html:
            errors.append(f"missing required CSS selector {selector}")
    article_files = sorted((root_path / "articles").glob("*.html")) if (root_path / "articles").exists() else []
    for article in article_files:
        href = f"articles/{article.name}"
        if href not in html:
            errors.append(f"homepage missing article link {href}")
    linked = re.findall(r"href=['\"]articles/([^'\"]+\.html)['\"]", html)
    for linked_name in linked:
        if not (root_path / "articles" / linked_name).exists():
            errors.append(f"homepage links missing article file {linked_name}")
    cards = re.findall(r"<article class='post-card'>.*?</article>", html, re.S)
    numbers = []
    for card in cards:
        match = re.search(r"Essay (\d+)", card)
        if match:
            numbers.append(int(match.group(1)))
    if numbers and numbers[0] != max(numbers):
        errors.append("top homepage card does not have highest Essay number")
    duplicate_titles = {title: files for title, files in existing_article_titles(root_path).items() if len(files) > 1}
    for title, files in sorted(duplicate_titles.items()):
        errors.append(f"duplicate article title {title}: {', '.join(sorted(files))}")
    duplicate_bodies = {fingerprint: files for fingerprint, files in existing_article_body_fingerprints(root_path).items() if len(files) > 1}
    for fingerprint, files in sorted(duplicate_bodies.items()):
        errors.append(f"duplicate article body {fingerprint[:12]}: {', '.join(sorted(files))}")
    for score, left_name, right_name in near_duplicate_article_bodies(root_path):
        errors.append(f"near-duplicate article body {score:.2f}: {left_name}, {right_name}")
    return {"ok": not errors, "errors": errors, "article_count": len(article_files), "linked_count": len(linked)}


def publish_one_ready_draft(*, root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root)
    ready_dir = root_path / "drafts" / "ready"
    draft_path = _first_ready_draft(ready_dir)
    if draft_path is None:
        return {"ok": False, "status": "NO_READY_DRAFT", "errors": ["no drafts/ready/*.json found"]}

    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    existing_titles = existing_article_titles(root_path)
    draft_title = str(draft.get("title", ""))
    draft_filename = f"{draft.get('slug')}.html"
    if draft_title in existing_titles and draft_filename not in existing_titles[draft_title]:
        return {"ok": False, "status": "DUPLICATE_TITLE", "errors": [f"title already published: {draft_title}"]}
    existing_bodies = existing_article_body_fingerprints(root_path)
    draft_body = str(draft.get("body_html", ""))
    draft_body_fingerprint = _body_fingerprint(draft_body)
    if draft_body_fingerprint in existing_bodies and draft_filename not in existing_bodies[draft_body_fingerprint]:
        return {"ok": False, "status": "DUPLICATE_BODY", "errors": [f"article body already published: {', '.join(sorted(existing_bodies[draft_body_fingerprint]))}"]}
    draft_shingles = _word_shingles(draft_body)
    near_matches = []
    for article_name, article_shingles in existing_article_body_shingles(root_path).items():
        if article_name == draft_filename:
            continue
        score = _jaccard(draft_shingles, article_shingles)
        if score >= 0.72:
            near_matches.append((score, article_name))
    if near_matches:
        score, article_name = sorted(near_matches, reverse=True)[0]
        return {"ok": False, "status": "NEAR_DUPLICATE_BODY", "errors": [f"article body too similar to {article_name}: {score:.2f}"]}
    validation = validate_draft_article(draft, source_cache_dir=root_path / "source_cache")
    if not validation["ok"]:
        return {"ok": False, "status": "DRAFT_INVALID", "errors": validation["errors"], "draft": str(draft_path)}

    article_path = render_article_file(draft, output_dir=root_path / "articles")
    rendered_word_count = visible_word_count(article_path.read_text(encoding="utf-8"))
    receipt = create_receipt(draft, rendered_word_count)
    _atomic_write_json(root_path / "article_meta" / f"{draft['slug']}.json", receipt)
    if "topic" in draft:
        mark_topic_used(draft, root_path / "topics" / "used_topics.json")
    _run_generate(root_path)
    homepage = validate_homepage_links_and_order(root=root_path)
    if not homepage["ok"]:
        return {"ok": False, "status": "HOMEPAGE_INVALID", "errors": homepage["errors"], "slug": draft["slug"]}
    draft_path.unlink()
    return {
        "ok": True,
        "status": "PUBLISHED",
        "slug": draft["slug"],
        "title": draft["title"],
        "article_path": str(article_path),
        "receipt_path": str(root_path / "article_meta" / f"{draft['slug']}.json"),
        "visible_word_count": rendered_word_count,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish exactly one Exodus V2 ready draft.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = publish_one_ready_draft(root=args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
