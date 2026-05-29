"""Render validated Exodus draft JSON into article HTML."""

from __future__ import annotations

import argparse
import html
import json
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typing import Any, Iterable

import generate


def render_article_html(draft: dict[str, Any]) -> str:
    title = html.escape(str(draft["title"]))
    description = html.escape(str(draft.get("description", "")), quote=True)
    official_title = html.escape(str(draft.get("official_title", "")))
    official_year = html.escape(str(draft.get("official_year", "")))
    site_anchor = html.escape(str(draft.get("site_anchor", "https://exodus.orsontbadger.com")), quote=True)
    body_html = str(draft["body_html"])
    today = date.today().strftime("%B %d, %Y")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <title>{title} · Exodus Field Notes</title>
  <style>{generate.STYLE}</style>
</head>
<body class="article-page">
  <div class="site">
    <nav class="nav"><a class="brand" href="../">EXODUS FIELD NOTES</a><a class="pill" href="https://exodus.orsontbadger.com">Read the series</a></nav>
    <main class="article-wrap">
      <div class="article-kicker">{official_title} · {official_year} · Exodus Analysis · {today}</div>
      <h1>{title}</h1>
      <p class="article-dek">{description}</p>
      <div class="article-body">
{body_html}
      </div>
      <section class="sales-card">
        <h2>Read the book behind this field note</h2>
        <p>Start the Exodus series from the official book page and follow the collapse, mutiny, lunar resistance, and Altair-era survival arcs in order.</p>
        <a class="cta" href="{site_anchor}">Read {official_title}</a>
      </section>
    </main>
    <div class="sticky-cta"><strong>EXODUS</strong><span>Field notes are only the map.</span><a href="{site_anchor}">Open the book</a></div>
  </div>
</body>
</html>
"""


def render_article_file(draft: dict[str, Any], *, output_dir: str | Path = "articles") -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{draft['slug']}.html"
    path.write_text(render_article_html(draft), encoding="utf-8")
    return path


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render one Exodus draft JSON to article HTML.")
    parser.add_argument("draft_json")
    parser.add_argument("--output-dir", default="articles")
    args = parser.parse_args(list(argv) if argv is not None else None)
    draft = json.loads(Path(args.draft_json).read_text(encoding="utf-8"))
    path = render_article_file(draft, output_dir=args.output_dir)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
