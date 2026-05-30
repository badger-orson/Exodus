#!/usr/bin/env python3
"""Exodus Signal Archive static renderer.

Homepage renderer for the autonomous Exodus book-promotion blog. Article bodies
come from drafts and existing HTML; this file owns the shared visual system and
homepage shell.
"""

from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BOOKS = {
    "chaos-rising": {
        "title": "Chaos Rising",
        "year": "2082",
        "label": "Curfew State",
        "accent": "#A7A9FF",
        "dark": "#21106F",
        "mid": "#35238F",
        "anchor": "https://exodus.orsontbadger.com/#book-1",
        "blurb": "Curfew, compliance, forbidden learning, and the Freemen ark.",
    },
    "mutiny": {
        "title": "Mutiny",
        "year": "2102",
        "label": "Ark Fracture",
        "accent": "#B783FF",
        "dark": "#35106F",
        "mid": "#53219A",
        "anchor": "https://exodus.orsontbadger.com/#book-2",
        "blurb": "A generation ship survives launch. Trust does not.",
    },
    "moonbound": {
        "title": "MoonBound",
        "year": "2087",
        "label": "Lunar Prison",
        "accent": "#E66BFF",
        "dark": "#4A0D5A",
        "mid": "#6C2082",
        "anchor": "https://exodus.orsontbadger.com/#book-3",
        "blurb": "Lunar prisons, buried resistance, and escape where roads do not exist.",
    },
    "biorift": {
        "title": "BioRift",
        "year": "2898",
        "label": "Altair Rift",
        "accent": "#FF76BE",
        "dark": "#570D35",
        "mid": "#84245B",
        "anchor": "https://exodus.orsontbadger.com/#book-4",
        "blurb": "The far future learns new tools for old monsters.",
    },
    "sandrats": {
        "title": "SandRats",
        "year": "2898",
        "label": "Azaa Frontier",
        "accent": "#FF6F86",
        "dark": "#5A0D18",
        "mid": "#8B2432",
        "anchor": "https://exodus.orsontbadger.com/#book-5",
        "blurb": "The promised world has teeth, dust, water laws, and no mercy.",
    },
}

STYLE = r"""
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@600;700;800;900&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');
:root{--color-bg:#000;--surface:#080711;--surface-2:#111022;--glass:rgba(18,15,35,.72);--line:rgba(184,176,208,.16);--line-strong:rgba(232,224,240,.28);--text:#e8e0f0;--text-warm:#ede9e3;--muted:#9a8fb0;--accent:#b8b0d0;--hero:#e0e2f4;--hero-muted:#9496ac;--chaos:#A7A9FF;--mutiny:#B783FF;--moonbound:#E66BFF;--biorift:#FF76BE;--sandrats:#FF6F86;--book-accent:var(--chaos);--book-dark:#21106F;--book-mid:#35238F;--font-display:'Exo 2','Futura','Century Gothic',Arial,sans-serif;--font-body:'Rajdhani','Gill Sans','Optima',Arial,sans-serif;--font-mono:'Share Tech Mono','Courier New',monospace;--pad:clamp(1rem,3vw,2rem);--max:74rem;--read:46rem;--radius:22px;--shadow:0 24px 90px rgba(0,0,0,.45)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;min-height:100vh;background:#000;color:var(--text);font-family:var(--font-body);font-size:clamp(1rem,1.2vw,1.125rem);line-height:1.65;overflow-x:hidden;-webkit-font-smoothing:antialiased}body:before{content:'';position:fixed;inset:0;z-index:-3;pointer-events:none;background:radial-gradient(ellipse at 16% 10%,rgba(96,72,235,.48),transparent 38%),radial-gradient(ellipse at 76% 22%,rgba(160,45,190,.32),transparent 34%),radial-gradient(ellipse at 50% 100%,rgba(210,50,72,.28),transparent 44%),linear-gradient(180deg,#000 0%,#070611 28%,#120d2d 58%,#050102 100%)}body:after{content:'';position:fixed;inset:0;z-index:-2;pointer-events:none;opacity:.23;background-image:linear-gradient(rgba(184,176,208,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(184,176,208,.05) 1px,transparent 1px),url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.12'/%3E%3C/svg%3E");background-size:72px 72px,72px 72px,512px 512px}a{color:inherit;text-decoration:none}a:focus-visible{outline:2px solid var(--book-accent);outline-offset:4px;border-radius:8px}.site{position:relative;z-index:1}.site:before{content:'EXODUS';position:fixed;left:50%;top:42%;transform:translate(-50%,-50%);z-index:-1;font-family:var(--font-display);font-size:clamp(6rem,22vw,18rem);font-weight:900;letter-spacing:.08em;color:rgba(232,224,240,.035);white-space:nowrap;pointer-events:none}.nav{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;gap:1rem;max-width:var(--max);margin:0 auto;padding:.85rem var(--pad);font-family:var(--font-mono);font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);backdrop-filter:blur(12px)}.brand{display:flex;align-items:center;gap:.55rem;color:var(--text);font-weight:700}.brand:before{content:'';width:.72rem;height:.72rem;border:1px solid var(--accent);border-radius:50%;box-shadow:0 0 24px rgba(184,176,208,.5)}.nav-links{display:flex;align-items:center;gap:.65rem;flex-wrap:wrap}.pill,.cta,.read-more{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;border:1px solid rgba(184,176,208,.28);border-radius:999px;background:rgba(8,7,17,.72);color:var(--text);padding:.55rem .9rem;font-family:var(--font-display);font-size:.76rem;font-weight:700;letter-spacing:.11em;text-transform:uppercase;transition:transform .25s ease,border-color .25s ease,background .25s ease,box-shadow .25s ease}.pill:hover,.cta:hover,.read-more:hover{transform:translateY(-1px);border-color:var(--book-accent);box-shadow:0 0 32px color-mix(in srgb,var(--book-accent) 28%,transparent)}.hero{max-width:var(--max);margin:0 auto;padding:clamp(4.5rem,9vw,8rem) var(--pad) clamp(2.5rem,5vw,4rem);display:grid;grid-template-columns:minmax(0,1.15fr) minmax(18rem,.85fr);gap:clamp(2rem,6vw,5rem);align-items:end}.eyebrow,.article-kicker,.post-meta,.timeline-year,.section-note{font-family:var(--font-mono);font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--book-accent)}.hero h1{margin:.7rem 0 1rem;font-family:var(--font-display);font-weight:900;line-height:.9;font-size:clamp(3.3rem,10vw,8rem);letter-spacing:.035em;text-transform:uppercase;color:var(--hero);text-shadow:0 0 50px rgba(189,189,255,.22)}.gradient{display:block;background:linear-gradient(100deg,var(--chaos),var(--moonbound),var(--sandrats));-webkit-background-clip:text;background-clip:text;color:transparent}.lede{max-width:46rem;margin:0 0 1.5rem;color:#c8c1d7;font-size:clamp(1.2rem,2vw,1.55rem);line-height:1.45}.hero-actions{display:flex;gap:.8rem;flex-wrap:wrap}.cta{background:linear-gradient(135deg,rgba(189,189,255,.2),rgba(248,186,216,.12));border-color:rgba(232,224,240,.38)}.timeline-card{position:relative;padding:1.2rem;border:1px solid var(--line);border-radius:var(--radius);background:linear-gradient(180deg,rgba(24,16,74,.52),rgba(8,7,17,.74));box-shadow:var(--shadow);overflow:hidden}.timeline-card:before{content:'';position:absolute;inset:-40% -20% auto auto;width:16rem;height:16rem;border:1px solid rgba(184,176,208,.16);border-radius:50%;box-shadow:0 0 0 34px rgba(184,176,208,.045),0 0 0 68px rgba(184,176,208,.025)}.timeline-item{position:relative;display:grid;grid-template-columns:4rem 1fr;gap:1rem;padding:.8rem 0;border-bottom:1px solid var(--line)}.timeline-item:last-child{border-bottom:0}.timeline-year{color:var(--item-accent,var(--accent))}.timeline-title{font-family:var(--font-display);font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:var(--text)}.timeline-label{color:var(--muted);font-size:.95rem}.section{max-width:var(--max);margin:0 auto;padding:clamp(2.5rem,6vw,5rem) var(--pad)}.section-head{display:flex;align-items:end;justify-content:space-between;gap:1rem;margin-bottom:1.25rem}.section h2{margin:0;font-family:var(--font-display);font-size:clamp(1.6rem,4vw,3rem);line-height:1;text-transform:uppercase;letter-spacing:.08em;color:var(--hero)}.feature-grid{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(16rem,.9fr);gap:1rem;margin-bottom:1rem}.featured-card,.book-card,.post-card,.sales-card{position:relative;border:1px solid var(--line);border-radius:var(--radius);background:linear-gradient(180deg,rgba(18,15,35,.78),rgba(8,7,17,.9));box-shadow:var(--shadow);overflow:hidden}.featured-card{min-height:24rem;padding:clamp(1.25rem,3vw,2rem);display:flex;flex-direction:column;justify-content:flex-end;background:radial-gradient(circle at 20% 0,color-mix(in srgb,var(--book-accent) 22%,transparent),transparent 38%),linear-gradient(160deg,color-mix(in srgb,var(--book-dark) 82%,#000),#05040b 72%)}.featured-card:before,.post-card:before,.article-wrap:before{content:'';position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,var(--book-accent),transparent)}.featured-card h2{font-size:clamp(2rem,5vw,4.2rem);letter-spacing:.03em;line-height:.96;margin:.6rem 0 1rem}.featured-card p{max-width:42rem;color:#d1cadd;font-size:1.16rem}.book-stack{display:grid;gap:1rem}.book-card{padding:1rem}.book-card h3{margin:.25rem 0;font-family:var(--font-display);letter-spacing:.09em;text-transform:uppercase;color:var(--item-accent,var(--text))}.book-card p{margin:0;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}.post-card{--book-accent:var(--card-accent,var(--accent));--book-dark:var(--card-dark,#18104A);display:flex;min-height:18rem;flex-direction:column;justify-content:space-between;padding:1.1rem;background:radial-gradient(circle at 24% 0,color-mix(in srgb,var(--book-accent) 18%,transparent),transparent 38%),linear-gradient(180deg,rgba(18,15,35,.82),rgba(5,4,11,.94))}.post-card h3{margin:.55rem 0 .7rem;font-family:var(--font-display);font-size:clamp(1.35rem,2.4vw,2rem);line-height:1.05;letter-spacing:.035em;text-transform:uppercase;color:var(--text)}.post-card p{margin:0;color:#bdb5ce}.post-card .read-more{align-self:flex-start;margin-top:1.2rem}.archive-empty{padding:2rem;border:1px solid var(--line);border-radius:var(--radius);color:var(--muted)}.article-page{--book-accent:var(--article-accent,var(--chaos));--book-dark:var(--article-dark,#18104A);padding-bottom:5.8rem}.article-wrap{position:relative;max-width:var(--read);margin:0 auto;padding:clamp(3rem,7vw,6rem) var(--pad);border-left:1px solid rgba(184,176,208,.08);border-right:1px solid rgba(184,176,208,.08);background:linear-gradient(180deg,rgba(8,7,17,.55),rgba(0,0,0,.08))}.article-wrap h1{margin:.75rem 0 1rem;font-family:var(--font-display);font-size:clamp(2.35rem,6vw,4.9rem);font-weight:900;line-height:1;letter-spacing:.025em;text-transform:uppercase;color:var(--hero)}.article-dek{margin:0 0 2rem;color:#c9c1d7;font-size:clamp(1.15rem,2vw,1.45rem);line-height:1.45}.article-body{font-size:1.16rem}.article-body p{margin:0 0 1.35rem}.article-body a{color:var(--book-accent);border-bottom:1px solid color-mix(in srgb,var(--book-accent) 50%,transparent)}.article-body h2{margin:2.4rem 0 1rem;font-family:var(--font-display);font-size:1.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--book-accent)}.sales-card{margin:3rem 0 0;padding:1.35rem;background:linear-gradient(145deg,color-mix(in srgb,var(--book-dark) 68%,#000),rgba(8,7,17,.92));border-color:color-mix(in srgb,var(--book-accent) 42%,transparent)}.sales-card h2{margin:0 0 .65rem;font-family:var(--font-display);text-transform:uppercase;letter-spacing:.08em}.sales-card p{margin:0 0 1rem;color:#cdc5d8}.sticky-cta{position:fixed;left:50%;bottom:.8rem;z-index:30;transform:translateX(-50%);width:min(calc(100% - 1rem),46rem);display:flex;align-items:center;justify-content:space-between;gap:.75rem;padding:.65rem .75rem;border:1px solid color-mix(in srgb,var(--book-accent) 42%,transparent);border-radius:999px;background:rgba(5,4,11,.88);box-shadow:0 18px 70px rgba(0,0,0,.45);backdrop-filter:blur(14px);font-family:var(--font-mono);font-size:.78rem;color:var(--muted)}.sticky-cta strong{font-family:var(--font-display);color:var(--text);letter-spacing:.14em}.sticky-cta a{padding:.45rem .7rem;border-radius:999px;background:var(--book-accent);color:#090711;font-family:var(--font-display);font-weight:800;text-transform:uppercase;letter-spacing:.08em}.footer{max-width:var(--max);margin:0 auto;padding:3rem var(--pad);color:var(--muted);font-family:var(--font-mono);font-size:.8rem;text-transform:uppercase;letter-spacing:.12em;border-top:1px solid var(--line)}
[data-book='chaos-rising']{--card-accent:#A7A9FF;--card-dark:#21106F;--article-accent:#A7A9FF;--article-dark:#21106F}[data-book='mutiny']{--card-accent:#B783FF;--card-dark:#35106F;--article-accent:#B783FF;--article-dark:#35106F}[data-book='moonbound']{--card-accent:#E66BFF;--card-dark:#4A0D5A;--article-accent:#E66BFF;--article-dark:#4A0D5A}[data-book='biorift']{--card-accent:#FF76BE;--card-dark:#570D35;--article-accent:#FF76BE;--article-dark:#570D35}[data-book='sandrats']{--card-accent:#FF6F86;--card-dark:#5A0D18;--article-accent:#FF6F86;--article-dark:#5A0D18}
body.is-reading .sticky-cta{width:min(13.5rem,calc(100% - 1rem));left:auto;right:.75rem;bottom:.75rem;transform:none;justify-content:center;padding:.5rem;border-radius:999px;opacity:.86}body.is-reading .sticky-cta span{display:none}body.is-reading .sticky-cta strong{font-size:.68rem}body.is-reading .sticky-cta a{padding:.38rem .6rem;font-size:.68rem}.sticky-cta{transition:width .24s ease,left .24s ease,right .24s ease,bottom .24s ease,transform .24s ease,opacity .24s ease,padding .24s ease,border-radius .24s ease}
@media(max-width:920px){.hero,.feature-grid{grid-template-columns:1fr}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.timeline-card{max-width:36rem}}@media(max-width:640px){.nav{position:relative;align-items:flex-start;flex-direction:column}.hero{padding-top:3rem}.grid{grid-template-columns:1fr}.section-head{align-items:flex-start;flex-direction:column}.featured-card{min-height:20rem}.sticky-cta{border-radius:18px;align-items:flex-start;flex-direction:column}.sticky-cta a{width:100%}}
"""


def _strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(value))).strip()


def _read_meta(slug: str) -> dict:
    path = ROOT / "article_meta" / f"{slug}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _extract_article(path: Path) -> dict:
    slug = path.stem
    text = path.read_text(encoding="utf-8", errors="ignore")
    meta = _read_meta(slug)
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
    desc_match = re.search(r'<meta name="description" content="([^"]*)"', text, re.S | re.I)
    title = _strip_tags(title_match.group(1)) if title_match else slug.replace("-", " ").title()
    excerpt = html.unescape(desc_match.group(1)).strip() if desc_match else "A sharp path into the Exodus series."
    book_slug = str(meta.get("book_slug") or _infer_book_slug(slug, text))
    book = BOOKS.get(book_slug, {})
    published = str(meta.get("published_at", ""))
    timestamp = path.stat().st_mtime
    if published:
        try:
            timestamp = datetime.fromisoformat(published.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    return {
        "slug": slug,
        "title": title,
        "excerpt": excerpt,
        "book_slug": book_slug,
        "book_title": str(meta.get("official_title") or book.get("title") or "Exodus"),
        "year": str(meta.get("official_year") or book.get("year") or ""),
        "label": str(book.get("label") or "Signal"),
        "anchor": str(book.get("anchor") or "https://exodus.orsontbadger.com"),
        "timestamp": timestamp,
    }


def _infer_book_slug(slug: str, text: str) -> str:
    haystack = f"{slug} {text[:2000]}".lower()
    for book_slug, book in BOOKS.items():
        if book_slug in haystack or str(book["title"]).lower() in haystack:
            return book_slug
    return "chaos-rising"


def discover_existing_articles() -> list[dict]:
    articles_dir = ROOT / "articles"
    if not articles_dir.is_dir():
        return []
    articles = [_extract_article(path) for path in articles_dir.glob("*.html")]
    return sorted(articles, key=lambda item: (item["timestamp"], item["slug"]), reverse=True)


def _timeline_html() -> str:
    rows = []
    for slug, book in BOOKS.items():
        rows.append(
            f"<a class='timeline-item' href='{html.escape(book['anchor'], quote=True)}' style='--item-accent:{book['accent']}'><div class='timeline-year'>{book['year']}</div><div><div class='timeline-title'>{html.escape(book['title'])}</div><div class='timeline-label'>{html.escape(book['label'])}</div></div></a>"
        )
    return "".join(rows)


def _book_cards_html() -> str:
    cards = []
    for slug, book in BOOKS.items():
        cards.append(
            f"<article class='book-card' data-book='{slug}' style='--item-accent:{book['accent']}'><div class='post-meta'>{book['year']} · {html.escape(book['label'])}</div><h3>{html.escape(book['title'])}</h3><p>{html.escape(book['blurb'])}</p></article>"
        )
    return "".join(cards)


def _article_card(article: dict, essay_number: int) -> str:
    return (
        f"<article class='post-card' data-book='{html.escape(article['book_slug'], quote=True)}'>"
        f"<div><div class='post-meta'>Signal {essay_number:03d} · {html.escape(article['book_title'])} · {html.escape(article['year'])}</div>"
        f"<h3>{html.escape(article['title'])}</h3><p>{html.escape(article['excerpt'])}</p></div>"
        f"<a class='read-more' href='articles/{html.escape(article['slug'], quote=True)}.html'>Read transmission</a></article>"
    )


def generate_homepage() -> None:
    articles = discover_existing_articles()
    total = len(articles)
    featured = articles[0] if articles else None
    cards = "".join(_article_card(article, total - index) for index, article in enumerate(articles))
    if not cards:
        cards = "<div class='archive-empty'>No transmissions published yet.</div>"
    feature_html = ""
    if featured:
        feature_html = (
            f"<a class='featured-card' data-book='{html.escape(featured['book_slug'], quote=True)}' href='articles/{html.escape(featured['slug'], quote=True)}.html'>"
            f"<div class='post-meta'>Featured Signal · {html.escape(featured['book_title'])} · {html.escape(featured['year'])}</div>"
            f"<h2>{html.escape(featured['title'])}</h2><p>{html.escape(featured['excerpt'])}</p><span class='read-more'>Read latest</span></a>"
        )
    html_text = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="The Exodus Signal Archive: dark reading paths through Orson T. Badger's five-book science fiction saga.">
  <title>Exodus Signal Archive · Orson T. Badger</title>
  <style>{STYLE}</style>
</head>
<body>
  <div class="site">
    <nav class="nav"><a class="brand" href="./">EXODUS SIGNAL ARCHIVE</a><div class="nav-links"><a class="pill" href="#transmissions">Transmissions</a><a class="pill" href="https://exodus.orsontbadger.com">Official series</a></div></nav>
    <header class="hero">
      <div>
        <div class="eyebrow">Orson T. Badger · Transmission archive</div>
        <h1>EXODUS <span class="gradient">SIGNALS</span></h1>
        <p class="lede">Sharp reading paths through curfew states, ark mutiny, lunar prisons, broken futures, and desert survival after the promised world fails.</p>
        <div class="hero-actions"><a class="cta" href="https://exodus.orsontbadger.com/#book-1">Start the Saga</a><a class="pill" href="#timeline">Explore Timeline</a></div>
      </div>
      <aside class="timeline-card" id="timeline" aria-label="Exodus timeline">{_timeline_html()}</aside>
    </header>
    <main>
      <section class="section" aria-labelledby="featured-heading">
        <div class="section-head"><h2 id="featured-heading">Latest Signal</h2><div class="section-note">Recovered reading path</div></div>
        <div class="feature-grid">{feature_html}<div class="book-stack">{_book_cards_html()}</div></div>
      </section>
      <section class="section" id="transmissions" aria-labelledby="archive-heading">
        <div class="section-head"><h2 id="archive-heading">Transmission Archive</h2><div class="section-note">{total} published signals</div></div>
        <div class="grid">{cards}</div>
      </section>
    </main>
    <footer class="footer">Dark essays and reading paths for the Exodus series · <a href="https://exodus.orsontbadger.com">exodus.orsontbadger.com</a></footer>
  </div>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html_text, encoding="utf-8")


if __name__ == "__main__":
    (ROOT / "articles").mkdir(exist_ok=True)
    generate_homepage()
    print(f"Generated Signal Archive homepage with {len(discover_existing_articles())} transmissions")
