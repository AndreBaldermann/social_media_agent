"""Domain models used by the social media workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class ArticleCandidate:
    """A link or article-like block found in the source HTML."""

    title: str
    url: str
    summary: str = ""


@dataclass(frozen=True)
class Article:
    """Normalized article content ready for post generation."""

    title: str
    url: str
    content: str
    source_hash: str


@dataclass(frozen=True)
class SocialDraft:
    """Draft posts for the supported channels."""

    article: Article
    linkedin: str
    twitter: str
    bluesky: str
    created_at: datetime

    @classmethod
    def create(cls, article: Article, linkedin: str, twitter: str, bluesky: str) -> SocialDraft:
        return cls(
            article=article,
            linkedin=linkedin,
            twitter=twitter,
            bluesky=bluesky,
            created_at=datetime.now(UTC),
        )
