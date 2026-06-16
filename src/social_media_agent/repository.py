"""Clone and summarize GitHub repositories for local LLM analysis."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from social_media_agent.models import RepositorySnapshot

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    "target",
    "coverage",
}
TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".rs",
    ".go",
    ".java",
    ".kt",
    ".cs",
    ".rb",
    ".php",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".sh",
    ".dockerfile",
}
IMPORTANT_NAMES = {
    "README",
    "README.md",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "Dockerfile",
    "docker-compose.yml",
    "compose.yml",
    ".github/workflows",
}


def clone_repository(repo_url: str, workspace_dir: Path, *, force: bool = False) -> Path:
    """Clone the repository URL into the workspace and return its local path."""

    workspace_dir.mkdir(parents=True, exist_ok=True)
    clone_dir = workspace_dir / _safe_repo_dir_name(repo_url)
    if clone_dir.exists():
        if not force:
            return clone_dir
        shutil.rmtree(clone_dir)
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(clone_dir)],
        check=True,
        text=True,
        capture_output=True,
    )
    return clone_dir


def build_snapshot(repo_url: str, clone_dir: Path, *, max_files: int = 80) -> RepositorySnapshot:
    """Build a compact, text-only snapshot of the cloned repository."""

    files = _iter_repo_files(clone_dir)
    file_tree = "\n".join(str(path.relative_to(clone_dir)) for path in files)
    selected_files: list[tuple[str, str]] = []
    for path in _rank_files(files, clone_dir)[:max_files]:
        content = _read_text(path)
        if content:
            selected_files.append((str(path.relative_to(clone_dir)), content[:12_000]))
            
    return RepositorySnapshot(
        repo_url=repo_url,
        clone_dir=clone_dir,
        file_tree=file_tree,
        selected_files=selected_files,
    )


def _safe_repo_dir_name(repo_url: str) -> str:
    parsed = urlparse(repo_url)
    name = Path(parsed.path.rstrip("/")).stem or "repository"
    digest = hashlib.sha1(repo_url.encode(), usedforsecurity=False).hexdigest()[:8]
    safe_name = "".join(char if char.isalnum() or char in "-_" else "-" for char in name)
    return f"{safe_name}-{digest}"


def _iter_repo_files(clone_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in clone_dir.rglob("*"):
        relative_parts = path.relative_to(clone_dir).parts
        if any(part in IGNORED_DIRS for part in relative_parts):
            continue
        if path.is_file() and _is_text_candidate(path):
            files.append(path)
    return sorted(files, key=lambda item: str(item.relative_to(clone_dir)))


def _is_text_candidate(path: Path) -> bool:
    if path.name in IMPORTANT_NAMES:
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def _rank_files(files: list[Path], clone_dir: Path) -> list[Path]:
    def score(path: Path) -> tuple[int, int, str]:
        relative = str(path.relative_to(clone_dir))
        basename = path.name
        priority = 50
        if basename.lower().startswith("readme"):
            priority = 0
        elif basename in {"pyproject.toml", "package.json", "Cargo.toml", "go.mod"}:
            priority = 1
        elif relative.startswith(".github/workflows"):
            priority = 2
        elif "test" in relative.lower():
            priority = 8
        elif path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".go", ".rs"}:
            priority = 4
        return (priority, len(relative), relative)

    return sorted(files, key=score)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")
