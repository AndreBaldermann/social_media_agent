"""Domain models for the repository analysis workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class RepositoryJob:
    """Input and workspace information for one repository analysis run."""

    repo_url: str
    clone_dir: Path
    output_dir: Path
    model: str
    context_window: int = 128_000


@dataclass(frozen=True)
class RepositorySnapshot:
    """Compact repository context passed to the local LLM."""

    repo_url: str
    clone_dir: Path
    file_tree: str
    selected_files: list[tuple[str, str]]


@dataclass(frozen=True)
class GeneratedAssets:
    """Generated review assets for the requested social channels."""

    html_report: str
    linkedin_text: str
    x_text: str
    bluesky_text: str
    created_at: datetime

    @classmethod
    def create(
        cls,
        html_report: str,
        linkedin_text: str,
        x_text: str,
        bluesky_text: str,
    ) -> GeneratedAssets:
        return cls(
            html_report=html_report,
            linkedin_text=linkedin_text,
            x_text=x_text,
            bluesky_text=bluesky_text,
            created_at=datetime.now(UTC),
        )


@dataclass(frozen=True)
class OutputPaths:
    """Paths written by the workflow."""

    html_report: Path
    linkedin_text: Path
    x_text: Path
    bluesky_text: Path
