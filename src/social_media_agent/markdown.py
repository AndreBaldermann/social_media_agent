"""Markdown output for human review."""

from __future__ import annotations

import re
from pathlib import Path

from social_media_agent.models import SocialDraft


def write_draft(draft: SocialDraft, output_dir: Path) -> Path:
    """Write a social draft as a reviewable Markdown file."""

    output_dir.mkdir(parents=True, exist_ok=True)
    date_prefix = draft.created_at.strftime("%Y-%m-%d")
    slug = _slugify(draft.article.title)
    path = output_dir / f"{date_prefix}-{slug}.md"
    path.write_text(_render_markdown(draft), encoding="utf-8")
    return path


def _render_markdown(draft: SocialDraft) -> str:
    return f"""# Social-Media-Entwurf: {draft.article.title}

- Quelle: {draft.article.url}
- Erstellt: {draft.created_at.isoformat()}
- Status: Entwurf / bitte manuell prüfen

## LinkedIn

{draft.linkedin}

## Twitter/X

{draft.twitter}

## Bluesky

{draft.bluesky}
"""


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:70] or "artikel"
