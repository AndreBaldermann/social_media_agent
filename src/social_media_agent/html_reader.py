"""Read article candidates from a local news.html file."""

from __future__ import annotations

import hashlib
import importlib.util
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

from social_media_agent.models import Article, ArticleCandidate

_HAS_BS4 = importlib.util.find_spec("bs4") is not None
if _HAS_BS4:
    from bs4 import BeautifulSoup


def read_candidates(news_html: Path) -> list[ArticleCandidate]:
    """Extract link-like article candidates from a local HTML file."""

    html = news_html.read_text(encoding="utf-8")
    if _HAS_BS4:
        return _read_candidates_with_bs4(html, news_html)
    return _read_candidates_with_stdlib(html, news_html)


def candidates_to_articles(candidates: list[ArticleCandidate]) -> list[Article]:
    """Normalize candidates into article objects with stable hashes."""

    articles: list[Article] = []
    for candidate in candidates:
        content = candidate.summary or candidate.title
        source_hash = hashlib.sha256(f"{candidate.url}\n{candidate.title}".encode()).hexdigest()
        articles.append(
            Article(
                title=candidate.title,
                url=candidate.url,
                content=content,
                source_hash=source_hash,
            )
        )
    return articles


def _read_candidates_with_bs4(html: str, news_html: Path) -> list[ArticleCandidate]:
    soup = BeautifulSoup(html, "html.parser")
    base_url = _base_url_bs4(soup, news_html)

    candidates: list[ArticleCandidate] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        title = anchor.get_text(" ", strip=True)
        if not title:
            continue
        url = urljoin(base_url, anchor["href"])
        if url in seen:
            continue
        seen.add(url)
        summary = _nearby_text(anchor)
        candidates.append(ArticleCandidate(title=title, url=url, summary=summary))

    if candidates:
        return candidates

    title = _page_title_bs4(soup, news_html)
    text = soup.get_text(" ", strip=True)
    if not text:
        return []
    return [ArticleCandidate(title=title, url=str(news_html), summary=text)]


def _base_url_bs4(soup, news_html: Path) -> str:  # noqa: ANN001 - optional BeautifulSoup typing.
    base = soup.find("base", href=True)
    if base:
        return str(base["href"])
    return news_html.resolve().as_uri()


def _page_title_bs4(soup, news_html: Path) -> str:  # noqa: ANN001 - optional BeautifulSoup typing.
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return news_html.stem


def _nearby_text(anchor) -> str:  # noqa: ANN001 - BeautifulSoup tag typing is intentionally loose.
    container = anchor.find_parent(["article", "li", "section", "div"])
    if not container:
        return anchor.get_text(" ", strip=True)
    return container.get_text(" ", strip=True)


class _NewsHTMLParser(HTMLParser):
    """Minimal stdlib fallback parser used when BeautifulSoup is unavailable."""

    def __init__(self, news_html: Path) -> None:
        super().__init__()
        self.base_url = news_html.resolve().as_uri()
        self.page_title = news_html.stem
        self._in_title = False
        self._current_href: str | None = None
        self._current_text: list[str] = []
        self._container_depth = 0
        self._container_text: list[str] = []
        self._container_candidate_indices: list[int] = []
        self.candidates: list[ArticleCandidate] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "base" and attributes.get("href"):
            self.base_url = attributes["href"] or self.base_url
        if tag == "title":
            self._in_title = True
        if tag in {"article", "li", "section", "div"}:
            self._container_depth += 1
            if self._container_depth == 1:
                self._container_text = []
                self._container_candidate_indices = []
        if tag == "a" and attributes.get("href"):
            self._current_href = attributes["href"]
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._current_href:
            title = " ".join(self._current_text).strip()
            if title:
                summary = " ".join(self._container_text).strip() or title
                self.candidates.append(
                    ArticleCandidate(
                        title=title,
                        url=urljoin(self.base_url, self._current_href),
                        summary=summary,
                    )
                )
                if self._container_depth:
                    self._container_candidate_indices.append(len(self.candidates) - 1)
            self._current_href = None
            self._current_text = []
        if tag in {"article", "li", "section", "div"} and self._container_depth:
            if self._container_depth == 1 and self._container_candidate_indices:
                summary = " ".join(self._container_text).strip()
                for index in self._container_candidate_indices:
                    candidate = self.candidates[index]
                    self.candidates[index] = ArticleCandidate(
                        title=candidate.title,
                        url=candidate.url,
                        summary=summary or candidate.summary,
                    )
            self._container_depth -= 1

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if not value:
            return
        if self._in_title:
            self.page_title = value
        if self._current_href:
            self._current_text.append(value)
        if self._container_depth:
            self._container_text.append(value)


def _read_candidates_with_stdlib(html: str, news_html: Path) -> list[ArticleCandidate]:
    parser = _NewsHTMLParser(news_html)
    parser.feed(html)
    if parser.candidates:
        seen: set[str] = set()
        unique: list[ArticleCandidate] = []
        for candidate in parser.candidates:
            if candidate.url in seen:
                continue
            seen.add(candidate.url)
            unique.append(candidate)
        return unique
    text = " ".join(part.strip() for part in html.split() if part.strip())
    if not text:
        return []
    return [ArticleCandidate(title=parser.page_title, url=str(news_html), summary=text)]
