"""SQLite persistence for processed articles."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from social_media_agent.models import Article

SCHEMA = """
CREATE TABLE IF NOT EXISTS processed_articles (
    source_hash TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    markdown_path TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class ArticleStore:
    """Small SQLite wrapper for idempotent article processing."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            connection.executescript(SCHEMA)

    def has_article(self, source_hash: str) -> bool:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT 1 FROM processed_articles WHERE source_hash = ?",
                (source_hash,),
            ).fetchone()
        return row is not None

    def remember(self, article: Article, markdown_path: Path) -> None:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO processed_articles (source_hash, title, url, markdown_path)
                VALUES (?, ?, ?, ?)
                """,
                (article.source_hash, article.title, article.url, str(markdown_path)),
            )
