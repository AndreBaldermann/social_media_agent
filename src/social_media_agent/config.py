"""Runtime configuration for the local Ollama workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "qwen3-coder-next:latest"
DEFAULT_CONTEXT_WINDOW = 128_000


@dataclass(frozen=True)
class Settings:
    """CLI settings for one repository analysis run."""

    repo_url: str
    workspace_dir: Path = Path("workspace/repos")
    output_dir: Path = Path("output")
    model: str = DEFAULT_MODEL
    context_window: int = DEFAULT_CONTEXT_WINDOW
    force: bool = False

    @classmethod
    def from_args(
        cls,
        repo_url: str,
        workspace_dir: str,
        output_dir: str,
        model: str,
        context_window: int,
        force: bool,
    ) -> Settings:
        return cls(
            repo_url=repo_url,
            workspace_dir=Path(workspace_dir),
            output_dir=Path(output_dir),
            model=model,
            context_window=context_window,
            force=force,
        )
