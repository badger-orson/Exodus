# Exodus Blog V2 Editorial Pipeline Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Replace the queue-only Exodus blog publisher with a source-grounded editorial pipeline that reads available EPUBs, selects real book-backed topics, creates a thesis, drafts a human-feeling essay, validates source/metadata/style, and publishes one field note per run.

**Architecture:** Split the system into small deterministic scripts plus agent-facing JSON artifacts. Python stdlib handles EPUB extraction and validation. The LLM/agent work happens only at the topic/draft/editorial stages, with source chunks and validation sidecars proving what material supported each article.

**Tech Stack:** Python 3.11 stdlib, `unittest`, JSON artifacts, existing static HTML/CSS, existing GitHub Pages deployment.

---

## V2 Directory Layout

Create these paths:

```text
source_cache/                 # generated source chunks from EPUBs, committed only if useful
source_cache/books.json       # book/chapter/chunk index
source_cache/chunks/*.json    # chunk files by book slug

topics/
  candidates.json             # source-backed topic candidates
  used_topics.json            # published/retired topic ledger

drafts/
  ready/*.json                # validated draft payloads waiting to publish
  rejected/*.json             # failed drafts with reason

article_meta/                 # source receipts for published articles
  <slug>.json

scripts/
  exodus_common.py            # shared metadata, HTML/text helpers
  extract_sources.py          # EPUB -> clean chunks
  validate_sources.py         # source cache sanity checks
  scout_topic.py              # source chunks -> topic candidate skeleton
  validate_topic.py           # topic must have thesis + source chunks
  render_article.py           # draft JSON -> article HTML
  validate_article.py         # word count, metadata, CSS, source receipt, forbidden terms
  publish_ready.py            # publish exactly one ready draft
  run_editorial_cycle.py      # top-level V2 cron entrypoint

tests/
  fixtures/
  test_extract_sources.py
  test_topic_validation.py
  test_article_validation.py
  test_publish_ready.py
```

Existing files to keep:

```text
generate.py                   # homepage rendering and shared STYLE, may be refactored later
exodus_metadata.json          # official metadata map, remains source of truth for titles/dates/anchors
articles/*.html               # published article pages
index.html                    # homepage
```

Retired V1 file after V2 verification:

```text
publish_one.py                # deleted after V2 published successfully and cron moved to scripts/run_editorial_cycle.py
```

Do not restore V1 unless rolling back the V2 cron and V2 publishing stack.

---

## Data Contracts

### Source Chunk

```json
{
  "id": "chaos-rising:0007",
  "book_slug": "chaos-rising",
  "official_title": "Chaos Rising",
  "official_year": 2082,
  "source_path": "/home/badgero1234/exodus-books/Exodus_ Leaving Home - Orson T Badger.epub",
  "spine_index": 7,
  "text": "clean visible text from the EPUB chunk",
  "word_count": 420,
  "entities": ["David Corb", "Freemen", "Compliance Army"],
  "themes": ["forbidden learning", "curfew", "resistance"]
}
```

### Topic Candidate

```json
{
  "id": "chaos-rising-forbidden-learning-resistance",
  "book_slug": "chaos-rising",
  "official_title": "Chaos Rising",
  "official_year": 2082,
  "topic": "Forbidden learning as resistance",
  "thesis": "Chaos Rising makes education dangerous because knowledge is the first thing a control regime has to ration.",
  "source_chunks": ["chaos-rising:0007", "chaos-rising:0011"],
  "concrete_details": ["curfew pressure", "David studying after work", "Freemen technical recruitment"],
  "why_readers_care": "This frames the novel as a resistance story built from competence before combat."
}
```

### Draft Article

```json
{
  "slug": "chaos-rising-education-as-contraband",
  "title": "The First Rebellion Is Learning Something Forbidden",
  "description": "A Chaos Rising field note on forbidden education, technical competence, and why the Freemen resistance begins before the ark launches.",
  "book_slug": "chaos-rising",
  "official_title": "Chaos Rising",
  "official_year": 2082,
  "site_anchor": "https://exodus.orsontbadger.com/#book-1",
  "topic_id": "chaos-rising-forbidden-learning-resistance",
  "thesis": "Chaos Rising makes education dangerous because knowledge is the first thing a control regime has to ration.",
  "source_chunks": ["chaos-rising:0007", "chaos-rising:0011"],
  "body_html": "<p>...</p>",
  "visible_word_count": 930
}
```

### Published Source Receipt

```json
{
  "slug": "chaos-rising-education-as-contraband",
  "published_at": "ISO-8601 timestamp",
  "book_slug": "chaos-rising",
  "official_title": "Chaos Rising",
  "official_year": 2082,
  "topic_id": "chaos-rising-forbidden-learning-resistance",
  "thesis": "Chaos Rising makes education dangerous because knowledge is the first thing a control regime has to ration.",
  "source_chunks": ["chaos-rising:0007", "chaos-rising:0011"],
  "visible_word_count": 930,
  "commit": "filled after commit by cron/reporting step"
}
```

---

## Editorial Agents

The user does not need to manually hire agents. Muad'Dib coordinates these roles via subagents or a single run depending on context size.

### Librarian

Reads EPUBs and builds `source_cache`. It does not publish and does not write essays.

### Topic Scout

Reads source chunks and proposes one sharp topic with a thesis. It must cite chunk IDs and concrete details.

### Essayist

Writes the field note from the approved topic. It must write for humans: hook, thesis, concrete scene texture, rhythm, and earned CTA.

### Editor

Cuts bland prose, improves rhythm, checks the hook, removes generic filler, and rejects boring drafts.

### Source Guard

Verifies the article only uses supported details, official metadata is correct, old draft titles/dates are not visible, and source chunk IDs exist.

### Publisher

Renders HTML, updates homepage, validates order/numbering/links/CSS, commits, pushes, and reports.

---

## Non-Negotiable Gates

### Pre-flight Gate

Before any article generation:

- `exodus_metadata.json` exists and parses.
- Every metadata `epub` path exists.
- `source_cache/books.json` exists or can be regenerated.
- Official public title/year/anchor exists for the selected book.

### Topic Gate

Before drafting:

- topic has a non-generic thesis.
- topic cites at least 2 source chunks.
- topic includes at least 3 concrete details.
- topic is not already in `topics/used_topics.json`.

### Draft Gate

Before rendering:

- 800-1200 visible words.
- no emdash.
- no forbidden old titles/dates in visible text.
- official title, official year, and CTA anchor present.
- body includes concrete details from source chunks.
- voice is human, not summary sludge.

### Publish Gate

Before commit/push:

- article HTML exists.
- article metadata sidecar exists.
- homepage links all article files.
- every linked article exists.
- newest article appears first.
- newest article has the highest Field Note number.
- required CSS selectors exist: `.grid`, `.article-wrap`, `.post-card`, `.sticky-cta`, `.sales-card`.
- `git diff --check` passes.

---

## Task 1: Add Shared Common Utilities and Tests

**Objective:** Create testable helpers for metadata loading, visible text extraction, word count, forbidden text checks, and slug normalization.

**Files:**
- Create: `scripts/exodus_common.py`
- Create: `tests/test_exodus_common.py`

**Test command:**

```bash
python3 -m unittest tests.test_exodus_common -v
```

**Expected behaviors:**

- strip HTML/style to visible text.
- count visible words.
- detect emdash and forbidden strings.
- load metadata and expose books by official title and slug.

---

## Task 2: Add EPUB Source Extraction

**Objective:** Extract readable text from EPUBs using Python stdlib only.

**Files:**
- Create: `scripts/extract_sources.py`
- Create: `tests/test_extract_sources.py`

**Test command:**

```bash
python3 -m unittest tests.test_extract_sources -v
```

**Implementation notes:**

- EPUB is a zip file.
- Read `.xhtml`, `.html`, `.htm` members.
- Strip tags using `html.parser`, not BeautifulSoup.
- Normalize whitespace.
- Split into chunks around 350-700 words.
- Write JSON atomically.

---

## Task 3: Add Source Cache Validation

**Objective:** Prove every book in metadata has chunks and every chunk has required fields.

**Files:**
- Create: `scripts/validate_sources.py`
- Create: `tests/test_validate_sources.py`

**Test command:**

```bash
python3 -m unittest tests.test_validate_sources -v
```

---

## Task 4: Add Topic Candidate and Used Topic Ledger

**Objective:** Track topic candidates and prevent repetition.

**Files:**
- Create: `scripts/validate_topic.py`
- Create: `topics/used_topics.json`
- Create: `tests/test_topic_validation.py`

**Test command:**

```bash
python3 -m unittest tests.test_topic_validation -v
```

---

## Task 5: Add Draft Validation

**Objective:** Validate article drafts before rendering or publishing.

**Files:**
- Create: `scripts/validate_article.py`
- Create: `tests/test_article_validation.py`

**Test command:**

```bash
python3 -m unittest tests.test_article_validation -v
```

---

## Task 6: Add Draft Rendering

**Objective:** Render one validated draft JSON into article HTML using existing style and CTA structure.

**Files:**
- Create: `scripts/render_article.py`
- Create: `tests/test_render_article.py`

**Test command:**

```bash
python3 -m unittest tests.test_render_article -v
```

---

## Task 7: Add V2 Publisher

**Objective:** Publish exactly one ready draft, create source receipt, update homepage, and verify order/numbering.

**Files:**
- Create: `scripts/publish_ready.py`
- Create: `tests/test_publish_ready.py`
- Modify: `generate.py` only if needed to make homepage rendering importable/testable.

**Test command:**

```bash
python3 -m unittest tests.test_publish_ready -v
```

---

## Task 8: Add Top-Level Editorial Cycle

**Objective:** Provide one cron entrypoint that creates or publishes one article per run.

**Files:**
- Create: `scripts/run_editorial_cycle.py`

**Behavior:**

- If `drafts/ready/*.json` exists, publish one.
- If no ready draft exists, report `NEEDS_AGENT_DRAFT` with exact required context: selected source chunks, candidate topic, and draft JSON schema.
- Do not silently no-op.

Reason: deterministic scripts should not pretend to be writers. Muad'Dib or a subagent handles the creative drafting step, then the scripts validate and publish.

---

## Task 9: Wire Cron to V2 After One Manual Success

**Objective:** Update the existing Exodus cron job only after V2 publishes one article successfully.

**Files:**
- No repo file necessarily changed. Use `cronjob update` for job `f10b0daac1aa`.

**Cron behavior:**

- Run `python3 scripts/run_editorial_cycle.py`.
- If it publishes, verify/commit/push/report.
- If it reports `NEEDS_AGENT_DRAFT`, spawn the editorial agents in this order: Librarian if cache missing, Topic Scout, Essayist, Editor, Source Guard, then rerun publisher.
- Report title, thesis, book/year, source chunks, word count, commit, raw URL, Pages status.

---

## Final Verification

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/extract_sources.py
python3 scripts/validate_sources.py
python3 scripts/run_editorial_cycle.py
python3 generate.py
python3 - <<'PY'
from pathlib import Path
import re
idx = Path('index.html').read_text(encoding='utf-8')
assert "Field Note" in idx
assert "articles/" in idx
assert ".post-card" in idx
print("homepage basic checks ok")
PY
git diff --check
git status --short
```

Only then update cron.
