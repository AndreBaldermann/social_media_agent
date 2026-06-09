"""Runtime configuration for the workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Paths and model settings used by the command line app."""

    news_html: Path = Path("news.html")
    database_path: Path = Path("data/social_media_agent.sqlite3")
    output_dir: Path = Path("drafts")
    model: str = "gpt-4.1-mini"
    dry_run: bool = False

    @classmethod
    def from_args(
        cls,
        news_html: str,
        database_path: str,
        output_dir: str,
        model: str,
        dry_run: bool,
    ) -> Settings:
        return cls(
            news_html=Path(news_html),
            database_path=Path(database_path),
            output_dir=Path(output_dir),
            model=model,
            dry_run=dry_run,
        )
