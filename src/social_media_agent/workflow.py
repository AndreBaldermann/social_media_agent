"""Workflow for cloning a GitHub repo and creating local Ollama assets."""

from __future__ import annotations

from social_media_agent.config import Settings
from social_media_agent.generator import OllamaClient, generate_assets
from social_media_agent.models import OutputPaths, RepositoryJob
from social_media_agent.repository import build_snapshot, clone_repository
from social_media_agent.writer import write_assets


def run(settings: Settings) -> OutputPaths:
    """Run the full GitHub-repository-to-social-assets workflow."""

    clone_dir = clone_repository(settings.repo_url, settings.workspace_dir, force=settings.force)
    job = RepositoryJob(
        repo_url=settings.repo_url,
        clone_dir=clone_dir,
        output_dir=settings.output_dir,
        model=settings.model,
        context_window=settings.context_window,
    )
    snapshot = build_snapshot(job.repo_url, job.clone_dir)
    client = OllamaClient(model=job.model, context_window=job.context_window)
    assets = generate_assets(snapshot, client)
    return write_assets(assets, job.output_dir, job.repo_url)
