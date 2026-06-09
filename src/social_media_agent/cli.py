"""Command line interface for the social media agent."""

from __future__ import annotations

import argparse
import importlib.util

from social_media_agent.config import Settings
from social_media_agent.storage import ArticleStore
from social_media_agent.workflow import run

_HAS_DOTENV = importlib.util.find_spec("dotenv") is not None


def main() -> None:
    if _HAS_DOTENV:
        importlib.import_module("dotenv").load_dotenv()
    parser = argparse.ArgumentParser(
        description="Generate reviewable social-media drafts from news.html"
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init-db", help="Create the SQLite database schema")
    init_parser.add_argument(
        "--db", default=str(Settings.database_path), help="SQLite database path"
    )

    run_parser = subparsers.add_parser("run", help="Run the LangGraph draft workflow")
    run_parser.add_argument(
        "--news-html", default=str(Settings.news_html), help="Path to news.html"
    )
    run_parser.add_argument(
        "--db", default=str(Settings.database_path), help="SQLite database path"
    )
    run_parser.add_argument(
        "--out", default=str(Settings.output_dir), help="Markdown output directory"
    )
    run_parser.add_argument(
        "--model",
        default=Settings.model,
        help="OpenAI chat model when OPENAI_API_KEY is set",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write drafts but do not mark articles as processed in SQLite",
    )

    args = parser.parse_args()
    if args.command == "init-db":
        settings = Settings.from_args("news.html", args.db, "drafts", Settings.model, False)
        ArticleStore(settings.database_path).initialize()
        print(f"Initialized database: {args.db}")
        return

    if args.command == "run":
        settings = Settings.from_args(args.news_html, args.db, args.out, args.model, args.dry_run)
        result = run(settings)
        if result["saved_paths"]:
            print("Created drafts:")
            for path in result["saved_paths"]:
                print(f"- {path}")
        else:
            print("No new articles found.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
