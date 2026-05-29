#!/usr/bin/env python3
"""Publish exactly one Exodus field note, using official metadata plus EPUB-derived story notes."""

from __future__ import annotations

import html
import json
import os
import re
import subprocess
from pathlib import Path

from generate import STYLE, generate_homepage

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
META = ROOT / "exodus_metadata.json"
FORBIDDEN = ["2032", "2034", "2035", "2036", "2037", "Leaving Home", "Reprisal", "Moonbreak", "Ragtags", "Sandrats of Azaa", "—"]

QUEUE = [
    {
        "book": "Chaos Rising",
        "slug": "chaos-rising-curfew-before-the-ark",
        "title": "Before the Ark, the Curfew Came First",
        "description": "A Chaos Rising field note on curfew, compliance patrols, forbidden learning, and the Freemen project that becomes the Exodus escape route.",
        "image": "https://picsum.photos/id/1011/1200/630",
        "body": """
        <p><strong>Chaos Rising</strong> works because it does not begin with a clean revolution. It begins with pressure. The world of 2082 is not only ruled by force. It is managed by routine: time readouts on buildings, curfew warnings over crowded streets, approved work contracts, identity checks, and compliance patrols that can turn an ordinary day into a sentence.</p>
        <p>That is the first hook. The book understands that tyranny rarely announces itself every morning with a speech. It becomes the background noise of life. Cindy Corb walking faster because curfew is minutes away tells the reader more than a page of exposition could. She is not in a battlefield. She is in a city where everyone has learned the same nervous calculation: get indoors, avoid attention, carry nothing that asks questions.</p>
        <p>David Corb gives the story its other pressure point. He is a mechanic working under hovercars, trying to stay alive inside a system that has already decided what kind of life he is allowed to have. The Enlightened League of Nations controls work, education, housing, and even the future shape of families. David wants air and flight. The regime wants obedience. That conflict is small enough to feel personal and large enough to explain the whole world.</p>
        <p>The strongest detail is the forbidden school. David studies after work because the legal path is closed. That single choice turns education into resistance. It also makes the later Freemen recruitment feel earned. When Strom speaks of a special project and looks for engineers and doctors, he is not recruiting action heroes. He is recruiting people who still know how to learn when learning has been made dangerous.</p>
        <p>Morstyn and the compliance apparatus give the danger a human face. The book does not treat the regime as a faceless machine. It puts cruelty in rooms, in hands, in officers who understand exactly how fear travels through a family. That matters because <strong>Chaos Rising</strong> is not only about escape from Earth. It is about what kind of people are produced by a society that rewards informing, punishes private thought, and calls submission peace.</p>
        <p>The Freemen answer that world with a project that sounds impossible: build an ark in secret, hide it near the Moon, and move people before the League can close the trap. The carrier named Paul Revere is not just a ship. It is a memory device. The name tells you what the Freemen think they are doing. They are warning a people who may not have much time left to wake up.</p>
        <p>Captain Hezekiah Andersen seeing sunrise over Earth from the nearly complete carrier gives the book one of its cleanest contrasts. Below him is the world the League claims to have perfected. Around him is a secret vessel built by people who have decided perfection is another word for prison. The ark is unfinished, vulnerable, and crowded with risk. It is still freer than the cities below.</p>
        <p>The military texture keeps the premise from floating away into abstraction. Shuttles carrying refugees, Wasp fighters launching near the ark, pilots forming up under pressure, and communication chatter around the Paul Revere all make the escape feel logistical before it feels symbolic. People have to be moved. Craft have to be loaded. Timing has to hold. One failure can strand hundreds.</p>
        <p>Miah's thread adds another kind of horror. The Enhanced Duplicate Combat Personnel are treated as assets before they are treated as people. Numbered bodies, copied faces, locker rooms, readiness drills, and the language of enhancement all show how the League turns identity into equipment. That detail makes the Freemen project feel morally urgent. Escape is not only about changing location. It is about preserving the idea that a person is more than a function assigned by power.</p>
        <p>That is where the sales hook lives. <strong>Chaos Rising</strong> is not a simple rebellion fantasy. It is a pressure cooker about families, mechanics, doctors, pilots, secret schools, and a resistance trying to turn technical competence into survival. The action matters because the systems behind it matter. The book asks whether ordinary people can still choose courage after a government has spent years teaching them that choice itself is illegal.</p>
        <p>If you want the Exodus saga at its source, start here. Read <strong>Chaos Rising</strong> and watch the first break in the League's control become the beginning of humanity's long flight outward.</p>
        """,
    },
    {
        "book": "BioRift",
        "slug": "biorift-ragtag-survival-is-not-clean",
        "title": "Survival Is Not Clean in the Altair Rift",
        "description": "A BioRift field note on broken crews, hard choices, and why the Exodus future still feels dangerous after arrival.",
        "image": "https://picsum.photos/id/1002/1200/630",
        "body": """
        <p><strong>BioRift</strong> carries Exodus into 2898 with a different kind of danger. The old flight from Earth has become history, but history has not made people wiser. The setting has changed. The pressure has not. Crews still fracture. Supplies still matter. The wrong person with the right access can still bend survival into a weapon.</p>
        <p>The appeal here is the ragged edge of civilization. This is not a polished future where humanity solved itself by reaching another system. It is a future where people brought their appetites, debts, grudges, and half-buried loyalties with them. The machinery is newer. The moral problems are ancient. That contrast gives the book its bite. You can cross impossible distances and still find yourself trapped with the same old human hungers.</p>
        <p>That makes the book useful for readers who like science fiction with dirt under its nails. The Altair-era story is not about a shining fleet moving in perfect order. It is about groups forced into proximity, people making ugly bargains, and survival plans that only work if nobody asks too many questions about the cost. Every sealed hatch, ration count, medical decision, and field report has social weight because each one decides who gets trusted and who gets treated like cargo.</p>
        <p>What keeps <strong>BioRift</strong> connected to the earlier Exodus books is the series obsession with systems under stress. Air, water, medical care, transport, chain of command, loyalty, and information all become contested resources. When those systems break, character is revealed fast. The generous become tired. The disciplined become dangerous. The frightened become unpredictable. Exodus has always been good at showing that collapse is not only smoke and wreckage. Collapse is the moment when an ordinary procedure stops working and someone with authority has to decide whose pain counts.</p>
        <p>The title points toward rupture, and the story earns that feeling. A rift is not only a place. It is a condition. The people in this era live inside gaps: between official maps and real terrain, between command claims and field truth, between old ideals and the brutal math of what can actually be saved. That is where the tension lives. The reader is never allowed to rest inside the comforting idea that the correct plan exists somewhere. Plans are made by tired people with partial information.</p>
        <p>The Altair future also sharpens the series theme of inheritance. By this point, the flight from Earth has become legend, but legend does not repair engines, treat infection, ration water, or settle disputes between desperate people. The descendants of survivors inherit more than courage. They inherit debt, trauma, habits of secrecy, and institutions built by people who were trying not to die. Some of those institutions protect life. Some protect power. <strong>BioRift</strong> is interested in what happens when nobody can tell the difference quickly enough.</p>
        <p>That is the kind of science fiction Exodus does best. It does not ask whether humanity can build impressive technology. It asks whether humans can remain human while depending on machines, sealed habitats, failing plans, and leaders who may be guessing under pressure. The hardware matters because the hardware is where ethics becomes practical. A valve, a med bay, a transport window, or a route through hostile territory can turn a moral debate into a deadline.</p>
        <p>For readers coming from <strong>Chaos Rising</strong>, the pleasure is seeing how far the consequences travel. The Freemen's flight was never a clean ending. It was a beginning. By 2898, the descendants of that break are still dealing with the same central question: what must be preserved, and what must be abandoned, when survival stops being theoretical? The answer changes with each era, but the pressure remains familiar. Someone always wants order badly enough to excuse cruelty. Someone else always has to decide whether resistance is worth the cost.</p>
        <p>That continuity is what makes <strong>BioRift</strong> more than a side trip. It is a far-future stress test for the Exodus promise. Escaping one prison did not make people free forever. It only gave them a chance to build better habits before the next crisis arrived. The book understands that freedom is maintenance. It has to be repaired, defended, argued over, and carried by people who are often exhausted.</p>
        <p><strong>BioRift</strong> belongs to readers who like their space opera tense, practical, and morally crowded. Start it when you want Exodus at its roughest edge, where nobody gets to pretend the future is safe just because Earth is far behind. Read it for broken crews, bad options, frontier pressure, and the unsettling reminder that survival is never clean when people are still people.</p>
        """,
    },
    {
        "book": "SandRats",
        "slug": "sandrats-desert-survival-after-the-promised-future",
        "title": "The Promised Future Still Has Teeth",
        "description": "A SandRats field note on desert survival, pressure, and the hard frontier that waits after Exodus reaches the far future.",
        "image": "https://picsum.photos/id/1003/1200/630",
        "body": """
        <p><strong>SandRats</strong> understands that arrival is not the same thing as safety. By 2898, Exodus has moved far beyond the first desperate break from Earth, but the series has not softened. The frontier is still hungry. The terrain still punishes mistakes. Communities still survive by reading danger before danger speaks.</p>
        <p>The book's power is in its refusal to make the far future clean. Dust, scarcity, heat, distance, and fragile alliances do more than decorate the setting. They shape behavior. A person who wastes water is not merely foolish. A person who misreads a stranger can get others killed. A settlement is only as strong as its weakest habit. In this kind of world, civilization is not a skyline. It is a checklist, a watch rotation, a repaired seal, and a rule everyone follows even when pride says otherwise.</p>
        <p>That is why the title matters. Sand rats are survivors, not conquerors. They live close to the ground. They know routes, shelters, caches, signals, and silences. They survive because they respect the environment more than their own pride. In Exodus terms, that makes them kin to every mechanic, medic, pilot, and fugitive who kept going when the official plan broke. The series has always honored practical competence. <strong>SandRats</strong> moves that competence into harsher terrain and asks what knowledge is worth when the map is incomplete.</p>
        <p>The far-future frame also gives the series room to ask a sharper question. If humanity escaped tyranny, collapse, and the long dark between worlds, why is survival still so hard? The answer is simple and unpleasant. People carry their old patterns with them. A new planet or frontier does not erase fear, ambition, greed, loyalty, or love. It only gives those forces new terrain. The desert does not create selfishness, but it exposes it. It does not create courage, but it leaves fewer places for cowardice to hide.</p>
        <p><strong>SandRats</strong> is built for readers who like frontier science fiction where every tool matters. Vehicles, shelters, weapons, water stores, maps, and local knowledge are not props. They are the difference between returning and becoming one more warning story. The action works because the background pressure never lets up. A chase is not only a chase when fuel, visibility, heat, and terrain all have opinions. A standoff is not only a standoff when both sides know the nearest help may be too far away to matter.</p>
        <p>The frontier also changes how trust works. In a crowded city, mistrust can hide inside bureaucracy. In open country, mistrust becomes logistics. Who knows the route? Who controls the water? Who can repair the vehicle? Who is calm enough to read the ground instead of the rumor? <strong>SandRats</strong> understands that social order can be fragile without being sentimental. People need each other, but need does not make them good. It only makes every alliance more dangerous.</p>
        <p>There is also a strong family resemblance to the earlier Exodus books. The same series that made curfew streets feel dangerous can make open desert feel watched. The same series that treated education and repair work as resistance can treat local survival knowledge as power. Nobody lives long here by accident. The drama comes from the gap between what official systems claim and what people on the ground know. That gap has been part of Exodus since the beginning.</p>
        <p>That connection matters for readers who want the saga to feel continuous. <strong>SandRats</strong> is not merely a change of scenery. It is Exodus translated into dust, heat, hunger, and frontier judgment. The old question remains: when the plan fails, who still knows how to act? The answer is rarely the loudest person in the room. It is usually the one who checked the seals, counted the supplies, remembered the route, and kept fear from making the next decision.</p>
        <p>That is the sales promise. <strong>SandRats</strong> takes the Exodus saga into a harsher frontier without losing the core concern: ordinary people under extraordinary pressure, making decisions with incomplete information and no guarantee that virtue will be rewarded. It is survival fiction with a science-fiction spine, built around the belief that small disciplines matter when the environment is ready to punish theatrical heroics.</p>
        <p>If you want the Altair-era side of Exodus, read <strong>SandRats</strong>. It is the reminder that the promised future still has teeth, and that survival belongs to the people disciplined enough to notice where the sand has shifted. Read it when you want the future to feel dangerous, practical, and earned one hard mile at a time.</p>
        """,
    },
]


def load_meta() -> dict:
    with META.open(encoding="utf-8") as f:
        return json.load(f)


def visible_words(markup: str) -> int:
    text = re.sub(r"<[^>]+>", " ", markup)
    text = html.unescape(text)
    return len(re.findall(r"\b[\w']+\b", text))


def book_meta(meta: dict, title: str) -> dict:
    for book in meta["books"]:
        if book["title"] == title:
            return book
    raise SystemExit(f"FAILED: metadata missing {title}")


def render_article(article: dict, book: dict) -> str:
    body = article["body"].strip()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(article['description'])}">
  <title>{html.escape(article['title'])} · Exodus Field Notes</title>
  <style>{STYLE}</style>
</head>
<body class="article-page">
  <div class="site">
    <nav class="nav"><a class="brand" href="../">EXODUS FIELD NOTES</a><a class="pill" href="{book['site_anchor']}">Read {html.escape(book['title'])}</a></nav>
    <main class="article-wrap">
      <div class="post-meta">{html.escape(book['title'])} · {book['official_year']} · Field Note</div>
      <h1>{html.escape(article['title'])}</h1>
      <p class="dek">{html.escape(article['description'])}</p>
      <img class="hero-img" src="{article['image']}" alt="Dark cinematic frontier landscape">
      <article class="content">
        {body}
        <section class="sales-card">
          <h2>Read the book</h2>
          <p>Start this part of the Exodus saga with <strong>{html.escape(book['title'])}</strong>, the official {book['official_year']} entry from Orson T. Badger.</p>
          <a class="cta" href="{book['site_anchor']}">Get {html.escape(book['title'])}</a>
        </section>
      </article>
    </main>
    <div class="sticky-cta"><strong>{html.escape(book['title'])}</strong><span>Official Exodus entry, <em>{book['official_year']}</em></span><a href="{book['site_anchor']}">Read now</a></div>
  </div>
</body>
</html>
"""


def validate(slug: str, html_text: str, article: dict, book: dict) -> int:
    text = re.sub(r"<style.*?</style>", " ", html_text, flags=re.S)
    visible = re.sub(r"<[^>]+>", " ", text)
    visible = html.unescape(visible)
    for bad in FORBIDDEN:
        if bad in visible:
            raise SystemExit(f"FAILED: forbidden visible text found: {bad}")
    if book["title"] not in visible or str(book["official_year"]) not in visible or book["site_anchor"] not in html_text:
        raise SystemExit("FAILED: official title/year/anchor missing")
    for selector in [".grid", ".article-wrap", ".post-card", ".sticky-cta", ".sales-card"]:
        if selector not in html_text:
            raise SystemExit(f"FAILED: CSS selector missing: {selector}")
    count = visible_words(visible)
    if not 800 <= count <= 1200:
        raise SystemExit(f"FAILED: visible word count {count} outside 800-1200")
    return count


def main() -> None:
    os.chdir(ROOT)
    ARTICLES.mkdir(exist_ok=True)
    meta = load_meta()
    for article in QUEUE:
        path = ARTICLES / f"{article['slug']}.html"
        if path.exists():
            continue
        book = book_meta(meta, article["book"])
        html_text = render_article(article, book)
        count = validate(article["slug"], html_text, article, book)
        path.write_text(html_text, encoding="utf-8")
        generate_homepage()
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        if f"articles/{article['slug']}.html" not in index:
            raise SystemExit("FAILED: homepage link missing after generation")
        print(f"PUBLISHED_DRAFT title={article['title']} book={book['title']} year={book['official_year']} words={count} path={path.relative_to(ROOT)}")
        return
    raise SystemExit("FAILED: article queue exhausted")


if __name__ == "__main__":
    main()
