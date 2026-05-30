"""Top-level deterministic Exodus V2 editorial cycle entrypoint."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typing import Any, Iterable

from scripts import exodus_common
from scripts.extract_sources import build_source_cache
from scripts.publish_ready import publish_one_ready_draft
from scripts.validate_article import validate_draft_article
from scripts.validate_topic import load_used_topic_ids
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
    "source_chunks": ["<selected_chunk_id_1>", "<selected_chunk_id_2>"],
    "concrete_details": ["detail one", "detail two", "detail three"],
    "body_html": "<p>800-1200 visible words with CTA anchor.</p>",
}


def _is_publishable_context_chunk(chunk: dict[str, Any]) -> bool:
    text = str(chunk.get("text", ""))
    if int(chunk.get("word_count", 0)) < 150:
        return False
    return not exodus_common.find_forbidden_visible_text(text)


def _site_anchor_for_book(root: Path, book_slug: str) -> str:
    metadata_path = root / "exodus_metadata.json"
    if metadata_path.exists():
        metadata = exodus_common.load_metadata(metadata_path)
        book = metadata.get("books_by_slug", {}).get(book_slug, {})
        if book.get("site_anchor"):
            return str(book["site_anchor"])
    return "https://exodus.orsontbadger.com"


def _article_exists(root: Path, slug: str) -> bool:
    return (root / "articles" / f"{slug}.html").exists() or (root / "article_meta" / f"{slug}.json").exists()


def _detail_phrases(text: str) -> list[str]:
    clean = " ".join(text.replace("\u2014", " ").split())
    candidates: list[str] = []
    patterns = [
        r"\bMiah\b",
        r"\bElias\b",
        r"\bSergeant Anders\b",
        r"\bEarthers\b",
        r"\bDome 3\b",
        r"\bArk Police\b",
        r"\bPortar\b",
        r"\btourniquet\b",
        r"\blift shaft\b",
        r"\bsecurity troops\b",
        r"\bag-workers\b",
        r"\breception counter\b",
        r"\boptical nerves\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, clean, flags=re.I)
        if match:
            phrase = match.group(0)
            if phrase not in candidates:
                candidates.append(phrase)
    if len(candidates) < 3:
        for phrase in re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", clean):
            if phrase not in candidates and not exodus_common.find_forbidden_visible_text(phrase):
                candidates.append(phrase)
            if len(candidates) >= 3:
                break
    fallback = ["Ark security", "survival under pressure", "systems breaking under stress"]
    for phrase in fallback:
        if len(candidates) >= 3:
            break
        if phrase not in candidates:
            candidates.append(phrase)
    return candidates[:3]


def _signal_variants(chunks: list[dict[str, Any]]) -> dict[str, str]:
    """Return visible, source-specific phrases so deterministic articles do not clone bodies."""
    joined_ids = ", ".join(str(chunk.get("id", "")) for chunk in chunks)
    excerpts: list[str] = []
    for chunk in chunks[:3]:
        text = " ".join(str(chunk.get("text", "")).replace("\u2014", " ").split())
        sentences = re.split(r"(?<=[.!?])\s+", text)
        candidate = ""
        for sentence in sentences:
            if 90 <= len(sentence) <= 260 and not exodus_common.find_forbidden_visible_text(sentence):
                candidate = sentence
                break
        if not candidate:
            candidate = text[:220]
        candidate = candidate.strip(" ,.;:")
        if candidate and candidate not in excerpts:
            excerpts.append(candidate)
    while len(excerpts) < 3:
        excerpts.append("the pressure stays local, practical, and hard to ignore")
    return {
        "source_ids": joined_ids,
        "source_line_1": excerpts[0],
        "source_line_2": excerpts[1],
        "source_line_3": excerpts[2],
    }


def _published_topic_ids(root: Path) -> set[str]:
    ids = set(load_used_topic_ids(root / "topics" / "used_topics.json"))
    meta_dir = root / "article_meta"
    if meta_dir.exists():
        for path in meta_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if data.get("topic_id"):
                ids.add(str(data["topic_id"]))
    return ids


def _select_context(root: Path, *, rng: Any | None = None, excluded_topic_ids: set[str] | None = None) -> dict[str, Any]:
    chunks_dir = root / "source_cache" / "chunks"
    selected: list[dict[str, Any]] = []
    chunks_by_book: dict[str, list[dict[str, Any]]] = {}
    used_topics = _published_topic_ids(root) | set(excluded_topic_ids or set())
    for chunk_file in sorted(chunks_dir.glob("*.json")):
        chunks = json.loads(chunk_file.read_text(encoding="utf-8"))
        for chunk in chunks:
            if not _is_publishable_context_chunk(chunk):
                continue
            topic_id = f"{chunk.get('book_slug')}-{chunk.get('id')}-article".replace(":", "-")
            slug = topic_id.replace("_", "-")
            if topic_id in used_topics or _article_exists(root, slug):
                continue
            item = {
                "id": chunk.get("id"),
                "book_slug": chunk.get("book_slug"),
                "official_title": chunk.get("official_title"),
                "official_year": chunk.get("official_year"),
                "text_excerpt": str(chunk.get("text", ""))[:900],
                "text": str(chunk.get("text", "")),
                "word_count": chunk.get("word_count"),
            }
            selected.append(item)
            chunks_by_book.setdefault(str(chunk.get("book_slug")), []).append(item)

    eligible_books = sorted(book_slug for book_slug, chunks in chunks_by_book.items() if len(chunks) >= 2)
    if not eligible_books:
        return {"selected_source_chunks": selected[:3], "draft_schema": DRAFT_SCHEMA}

    chooser = rng or random.SystemRandom()
    book_slug = chooser.choice(eligible_books)
    book_chunks = chunks_by_book[book_slug]
    lead = chooser.choice(book_chunks)
    lead_index = book_chunks.index(lead)
    ordered = [lead]
    for offset in range(1, len(book_chunks)):
        ordered.append(book_chunks[(lead_index + offset) % len(book_chunks)])
        if len(ordered) >= 3:
            break
    return {"selected_source_chunks": ordered, "draft_schema": DRAFT_SCHEMA}


def _published_titles(root: Path) -> set[str]:
    titles: set[str] = set()
    for article in (root / "articles").glob("*.html"):
        text = article.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
        if match:
            title = re.sub(r"<[^>]+>", " ", match.group(1))
            title = " ".join(html.unescape(title).split())
            if title:
                titles.add(title)
    return titles


def _numeric_suffix(value: str) -> int:
    numbers = re.findall(r"\d+", value)
    return int(numbers[-1]) if numbers else 0


def _catchy_title(official_title: str, topic_id: str, existing_titles: set[str]) -> str:
    title_bank = {
        "Chaos Rising": [
            "The First Thing Tyrants Kill Is Competence",
            "Before the Ark, the Curfew Came First",
            "The Rebellion Begins With a Hidden Lesson",
            "A Regime Fears the People Who Can Fix Things",
            "The Compliance Army Was Afraid of Memory",
        ],
        "Mutiny": [
            "The Ship Was Supposed to Save Humanity. Then Humanity Got Inside It",
            "A Generation Ship Is No Place for Betrayal",
            "The Ark Survived Launch. Trust Did Not",
            "When the Crew Turns the Lifeboat Into a Battlefield",
            "Two Trillion Miles From Earth, Human Nature Still Finds the Knife",
        ],
        "MoonBound": [
            "Prison Looks Different When It Has a Horizon",
            "The Moon Was Supposed to Be Where Resistance Died",
            "The Hole Could Not Bury the Freemen",
            "A Lunar Prison Makes Escape a Systems Problem",
            "Resistance Survives Where Roads Do Not Exist",
        ],
        "BioRift": [
            "The Future Does Not Save Us. It Gives the Monsters Better Tools",
            "Dome 3 Is Where the Clean Future Cracks",
            "In the Altair Rift, Survival Starts Before the Alarm",
            "The Monsters in BioRift Wear Systems Like Armor",
            "The Future Learned to File Fear as Procedure",
            "When Security Becomes the Weather",
            "The Ark Police Are Not the Scariest Thing in BioRift",
            "Survival Begins With Reading the Room",
            "A Shiny Future Still Needs Someone to Bleed in the Lift Shaft",
            "The Altair Rift Turns Competence Into a Weapon",
            "BioRift Makes Survival Industrial",
            "The Future Is Clean Until the Counter Turns Into a Checkpoint",
        ],
        "SandRats": [
            "The Promised World Was a Desert With Teeth",
            "The Frontier Does Not Care Who Was Promised a Future",
            "Water Is the First Law of the New World",
            "The Desert Teaches Faster Than Civilization",
            "Survival Gets Smaller and Meaner After Arrival",
        ],
    }
    titles = title_bank.get(official_title, [f"The Future Breaks Differently in {official_title}"])
    start = _numeric_suffix(topic_id) % len(titles)
    for offset in range(len(titles)):
        candidate = titles[(start + offset) % len(titles)]
        if candidate not in existing_titles:
            return candidate
    return f"{titles[start]} in {official_title} {_numeric_suffix(topic_id):04d}"


def _build_deterministic_draft(root: Path, selected: list[dict[str, Any]]) -> dict[str, Any]:
    if len(selected) < 2:
        raise ValueError("not enough publishable source chunks to build a draft")
    first = selected[0]
    book_slug = str(first["book_slug"])
    chunks = [chunk for chunk in selected if chunk.get("book_slug") == book_slug][:3]
    if len(chunks) < 2:
        raise ValueError("not enough same-book source chunks to build a draft")
    official_title = str(first["official_title"])
    official_year = int(first["official_year"])
    chunk_ids = [str(chunk["id"]) for chunk in chunks[:3]]
    lead_text = " ".join(str(chunk.get("text", "")) for chunk in chunks[:2])
    details = _detail_phrases(lead_text)
    topic_id = f"{book_slug}-{chunk_ids[0]}-article".replace(":", "-")
    slug = topic_id.replace("_", "-")
    site_anchor = _site_anchor_for_book(root, book_slug)
    title = _catchy_title(official_title, topic_id, _published_titles(root))
    thesis = f"{official_title} shows that survival in {official_year} belongs to people who can read danger clearly, act with discipline, and keep moving when every system around them starts lying."
    escaped = {
        key: html.escape(str(value))
        for key, value in {
            "official_title": official_title,
            "site_anchor": site_anchor,
            "detail_1": details[0],
            "detail_2": details[1],
            "detail_3": details[2],
            **_signal_variants(chunks),
        }.items()
    }
    body_html = f"""
<p>This reading starts from source chunks {escaped['source_ids']} and narrows in on {escaped['detail_1']}, {escaped['detail_2']}, and {escaped['detail_3']}: not as lore labels, but as pressure points. The selected passage opens with this kind of pressure: {escaped['source_line_1']}. That sentence-level texture is the reason this article exists. It gives the signal a different center than the last article instead of recycling the same safe overview.</p>
<p>{escaped['official_title']} places its pressure where survival fiction earns or loses trust: not in a speech, not in a clean victory, but in the moment when the people inside the system realize the system has already stopped protecting them. The official timeline puts this story in {official_year}, and this randomly selected part points toward a world where danger is not abstract. A second source beat sharpens the angle: {escaped['source_line_2']}. Those concrete details are warning lights. They show a society where fear has become procedure and where every ordinary room can turn into a checkpoint.</p>
<p>The strongest thing about this part of Exodus is the way competence becomes moral weight. Characters do not survive because the universe grants them mercy. They survive because someone notices the wrong face in a crowd, reads the threat before it becomes official, or improvises with whatever remains close at hand. The story keeps returning to practical action: security moving through crowds, workers disappearing below a dome, a wounded body handled with wire because proper equipment is not available. That texture matters because it makes the larger conflict feel lived in. Collapse is not just a background condition. It reaches the counter, the lift shaft, the patrol route, the body, and the next breath.</p>
<p>That is why {escaped['official_title']} works for readers who like survival stories with teeth. The book is not asking whether people are brave in the abstract. It asks whether they can stay useful while frightened. It asks whether hatred, grief, and old injuries can become a map instead of a trap. When a character recognizes a threat through memory, pain, or pattern, the scene turns survival into attention. The person who sees clearly first has a chance. The person who waits for permission may already be lost.</p>
<p>The story also keeps the politics grounded. The words around the action point to police power, hostage taking, lower levels, workers, security troops, and people who have learned to live underneath official comfort. That gives the Exodus universe its bite. The future is advanced enough to have domes, pads, altered bodies, and shipboard systems, but the old human questions remain. Who gets protected. Who gets used. Who gets named as a threat. Who gets treated as disposable until they become dangerous enough to notice.</p>
<p>Readers coming from post-collapse fiction will recognize the shape, but Exodus gives it a sharper industrial edge. The danger is not only hunger or weather. It is administration with weapons behind it. It is a culture that can file suffering into categories and keep moving. The result is a setting where rebellion does not need to announce itself with a banner. Sometimes rebellion is a hidden worker network. Sometimes it is a refusal to stay captured. Sometimes it is a wounded person making one more ugly repair because no clean option remains.</p>
<p>The best entry point into this book is the pressure itself. Watch how the story uses rooms, counters, shafts, crowds, and improvised choices. In this selected passage, the third source beat is the tell: {escaped['source_line_3']}. Watch how a personal vendetta sits beside a larger social fracture. Watch how the Ark and its divided populations turn every encounter into a test of perception. That is the reader promise here: not a shiny future, but a future where every tool, injury, and rumor carries weight.</p>
<p>The smaller details are doing the heavy lifting. {escaped['detail_1']} gives the conflict a human face. {escaped['detail_2']} ties the danger back to consequence and memory. {escaped['detail_3']} shows how quickly private fear can become organized force. None of those pieces need a lore lecture to matter. They matter because they sit inside action. A reader can feel the machinery of power working around the characters, and can also see where that machinery leaves gaps for desperate people to move through.</p>
<p>{escaped['official_title']} is worth reading because it treats survival as discipline rather than luck. It understands that systems fail in layers. First trust fails. Then procedure fails. Then language fails, because official labels no longer describe what people are living through. By the time violence becomes visible, the real break has already happened. The useful characters are the ones who felt the break early and adapted before the announcement arrived.</p>
<p>That makes the book useful as more than a plot machine. It becomes a study of pressure. The clean institutions are gone or compromised, but people still need water, shelter, safety, witnesses, exits, and someone willing to make an ugly repair before the next attack. Exodus keeps returning to that truth. Civilization is not proven by slogans. It is proven by whether anyone can keep another person alive when the lights flicker, the records lie, and the corridor ahead is no longer safe.</p>
<p>If that is the kind of science fiction you want, start from the official Exodus page and follow the series in order. The books are built around collapse, resistance, ugly competence, and the cost of staying alive when the future has stopped pretending to be clean. Read {escaped['official_title']} here: <a href=\"{escaped['site_anchor']}\">{escaped['site_anchor']}</a>.</p>
""".strip()
    return {
        "slug": slug,
        "title": title,
        "description": f"A provocative look at {official_title}, survival pressure, and the ugly choices that make the Exodus timeline hard to forget.",
        "book_slug": book_slug,
        "official_title": official_title,
        "official_year": official_year,
        "site_anchor": site_anchor,
        "topic_id": topic_id,
        "topic": "survival under pressure",
        "thesis": thesis,
        "source_chunks": chunk_ids,
        "concrete_details": details,
        "body_html": body_html,
    }


def run_editorial_cycle(*, root: str | Path = ".", allow_extract: bool = True, rng: Any | None = None, max_attempts: int = 20) -> dict[str, Any]:
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

    ready_dir = root_path / "drafts" / "ready"
    ready_dir.mkdir(parents=True, exist_ok=True)
    rejected_topic_ids: set[str] = set()
    last_context: dict[str, Any] = {"selected_source_chunks": [], "draft_schema": DRAFT_SCHEMA}
    last_result: dict[str, Any] | None = None
    for _attempt in range(max_attempts):
        context = _select_context(root_path, rng=rng, excluded_topic_ids=rejected_topic_ids)
        last_context = context
        try:
            draft = _build_deterministic_draft(root_path, context["selected_source_chunks"])
        except ValueError as exc:
            return {"ok": False, "status": "NEEDS_SOURCE_CHUNKS", "errors": [str(exc)], **context}

        validation = validate_draft_article(draft, source_cache_dir=root_path / "source_cache")
        if not validation["ok"]:
            printable = {key: value for key, value in validation.items() if key != "visible_text"}
            return {"ok": False, "status": "GENERATED_DRAFT_INVALID", "errors": validation["errors"], "validation": printable, "draft": draft, **context}

        draft_path = ready_dir / f"{draft['slug']}.json"
        draft_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        published = publish_one_ready_draft(root=root_path)
        if published.get("ok"):
            published["draft_generated"] = True
            published["source_chunks"] = draft["source_chunks"]
            published["thesis"] = draft["thesis"]
            return published
        last_result = published
        if published.get("status") not in {"DUPLICATE_TITLE", "DUPLICATE_BODY", "NEAR_DUPLICATE_BODY"}:
            return published
        rejected_topic_ids.add(str(draft["topic_id"]))
        try:
            draft_path.unlink()
        except FileNotFoundError:
            pass

    errors = ["could not generate a unique publishable article"]
    if last_result and last_result.get("errors"):
        errors.extend(str(error) for error in last_result["errors"])
    return {"ok": False, "status": "UNIQUE_DRAFT_EXHAUSTED", "errors": errors, **last_context}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one Exodus V2 editorial cycle.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--no-extract", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = run_editorial_cycle(root=args.root, allow_extract=not args.no_extract)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
