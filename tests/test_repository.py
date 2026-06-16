from pathlib import Path
from unittest.mock import patch

from social_media_agent.repository import build_snapshot, clone_repository


def test_clone_repository_reuses_existing_clone(tmp_path: Path) -> None:
    existing = tmp_path / "repo-6ed44226"
    existing.mkdir(parents=True)

    with patch("social_media_agent.repository.subprocess.run") as run:
        clone_dir = clone_repository("https://github.com/acme/repo", tmp_path)

    assert clone_dir == existing
    run.assert_not_called()


def test_build_snapshot_selects_important_text_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nBusiness ready notes", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='demo'", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('hello')", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "config").write_text("ignored", encoding="utf-8")

    snapshot = build_snapshot("https://github.com/acme/repo", repo)

    selected_paths = [path for path, _ in snapshot.selected_files]
    assert "README.md" in selected_paths
    assert "pyproject.toml" in selected_paths
    assert "src/app.py" in selected_paths
    assert ".git/config" not in snapshot.file_tree
