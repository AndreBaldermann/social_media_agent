"""Command line interface for the local repository social media agent."""

from __future__ import annotations

import argparse

from social_media_agent.config import DEFAULT_CONTEXT_WINDOW, DEFAULT_MODEL, Settings
from social_media_agent.workflow import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clone a GitHub repo and generate local Ollama social-media assets."
    )
    parser.add_argument("repo_url", help="GitHub repository URL to clone and analyze")
    parser.add_argument(
        "--workspace-dir",
        default=str(Settings.workspace_dir),
        help="Directory where repositories are cloned",
    )
    parser.add_argument(
        "--out",
        default=str(Settings.output_dir),
        help="Directory where generated files are written",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Local Ollama model to use",
    )
    parser.add_argument(
        "--ctx",
        type=int,
        default=DEFAULT_CONTEXT_WINDOW,
        help="Ollama context window, defaults to 128k",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete and re-clone the repository if it already exists locally",
    )

    args = parser.parse_args()
    settings = Settings.from_args(
        repo_url=args.repo_url,
        workspace_dir=args.workspace_dir,
        output_dir=args.out,
        model=args.model,
        context_window=args.ctx,
        force=args.force,
    )
    paths = run(settings)
    print("Generated files:")
    print(f"- HTML report: {paths.html_report}")
    print(f"- LinkedIn: {paths.linkedin_text}")
    print(f"- X: {paths.x_text}")
    print(f"- Bluesky: {paths.bluesky_text}")


if __name__ == "__main__":
    main()
