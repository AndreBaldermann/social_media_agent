"""Write generated repository assets to disk."""

from __future__ import annotations

import re
from pathlib import Path

from social_media_agent.models import GeneratedAssets, OutputPaths


def write_assets(assets: GeneratedAssets, output_dir: Path, repo_url: str) -> OutputPaths:
    """Persist the HTML report and plain-text social drafts."""

    run_dir = output_dir / _slugify(repo_url)
    run_dir.mkdir(parents=True, exist_ok=True)
    paths = OutputPaths(
        html_report=run_dir / "repo-report.html",
        linkedin_text=run_dir / "linkedin.txt",
        x_text=run_dir / "x.txt",
        bluesky_text=run_dir / "bluesky.txt",
    )
    paths.html_report.write_text(assets.html_report, encoding="utf-8")
    paths.linkedin_text.write_text(_plain_single_line(assets.linkedin_text), encoding="utf-8")
    paths.x_text.write_text(_plain_single_line(assets.x_text), encoding="utf-8")
    paths.bluesky_text.write_text(_plain_single_line(assets.bluesky_text), encoding="utf-8")
    return paths


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:90] or "repository"


def _plain_single_line(value: str) -> str:
    #return " ".join(value.replace("\r", " ").replace("\n", " ").split())
    return value
