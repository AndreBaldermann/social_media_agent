from pathlib import Path
from unittest.mock import patch

from social_media_agent.config import Settings
from social_media_agent.models import GeneratedAssets, RepositorySnapshot
from social_media_agent.workflow import run


def test_workflow_writes_all_requested_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    settings = Settings(
        repo_url="https://github.com/acme/repo",
        workspace_dir=tmp_path / "workspace",
        output_dir=tmp_path / "output",
    )
    snapshot = RepositorySnapshot(
        repo_url=settings.repo_url,
        clone_dir=repo,
        file_tree="README.md",
        selected_files=[("README.md", "# Demo")],
    )
    assets = GeneratedAssets.create(
        html_report="<html></html>",
        linkedin_text="LinkedIn Text",
        x_text="X Text",
        bluesky_text="Bluesky Text",
    )

    with (
        patch("social_media_agent.workflow.clone_repository", return_value=repo),
        patch("social_media_agent.workflow.build_snapshot", return_value=snapshot),
        patch("social_media_agent.workflow.generate_assets", return_value=assets),
    ):
        paths = run(settings)

    assert paths.html_report.read_text(encoding="utf-8") == "<html></html>"
    assert paths.linkedin_text.read_text(encoding="utf-8") == "LinkedIn Text"
    assert paths.x_text.read_text(encoding="utf-8") == "X Text"
    assert paths.bluesky_text.read_text(encoding="utf-8") == "Bluesky Text"
