"""Shared helpers for the Exodus blog editorial pipeline."""

from __future__ import annotations

import copy
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

DEFAULT_METADATA_PATH = Path(__file__).resolve().parents[1] / "exodus_metadata.json"
FORBIDDEN_VISIBLE_STRINGS = [
    "2032",
    "2034",
    "2035",
    "2036",
    "2037",
    "Leaving Home",
    "Reprisal",
    "Moonbreak",
    "Ragtags",
    "Sandrats of Azaa",
    "—",
]


class _VisibleTextParser(HTMLParser):
    """Small stdlib HTML-to-visible-text parser."""

    _HIDDEN_TAGS = {"script", "style", "title", "head"}
    _SPACE_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._hidden_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self._HIDDEN_TAGS:
            self._hidden_depth += 1
        elif tag in self._SPACE_TAGS:
            self._parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self._HIDDEN_TAGS and self._hidden_depth:
            self._hidden_depth -= 1
        elif tag in self._SPACE_TAGS:
            self._parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self._hidden_depth:
            self._parts.append(data)

    def text(self) -> str:
        return " ".join("".join(self._parts).split())


def visible_text_from_html(markup: str) -> str:
    """Return collapsed visible text from HTML, excluding head/script/style/title."""

    parser = _VisibleTextParser()
    parser.feed(markup or "")
    parser.close()
    return html.unescape(parser.text())


def visible_word_count(markup: str) -> int:
    """Count words in visible HTML text."""

    return len(re.findall(r"\b[\w']+\b", visible_text_from_html(markup)))


def find_forbidden_visible_text(
    markup: str, forbidden: list[str] | tuple[str, ...] = FORBIDDEN_VISIBLE_STRINGS
) -> list[str]:
    """Return forbidden strings found in visible text, preserving configured order."""

    visible = visible_text_from_html(markup)
    return [term for term in forbidden if term in visible]


def slugify_title(title: str) -> str:
    """Normalize an official title to a lowercase dash slug."""

    slug = re.sub(r"[^a-z0-9]+", "-", title.strip().lower())
    return slug.strip("-")


def load_metadata(path: str | Path = DEFAULT_METADATA_PATH) -> dict[str, Any]:
    """Load Exodus metadata and add books_by_title/books_by_slug indexes.

    Each indexed book is a shallow copy of the source book with a computed ``slug``
    based on its official ``title``.
    """

    metadata_path = Path(path)
    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    loaded: dict[str, Any] = copy.deepcopy(data)

    books_by_title: dict[str, dict[str, Any]] = {}
    books_by_slug: dict[str, dict[str, Any]] = {}
    indexed_books: list[dict[str, Any]] = []
    for book in loaded.get("books", []):
        indexed = dict(book)
        indexed["slug"] = slugify_title(str(indexed["title"]))
        indexed_books.append(indexed)
        books_by_title[indexed["title"]] = indexed
        books_by_slug[indexed["slug"]] = indexed

    loaded["books"] = indexed_books
    loaded["books_by_title"] = books_by_title
    loaded["books_by_slug"] = books_by_slug
    return loaded
