from pathlib import Path

from social_media_agent.config import Settings
from social_media_agent.workflow import run


def test_workflow_creates_markdown_and_skips_processed_articles(tmp_path: Path) -> None:
    news_html = tmp_path / "news.html"
    news_html.write_text(
        """
        <html><body>
          <article><a href="https://example.com/a">Artikel A</a><p>Inhalt A</p></article>
        </body></html>
        """,
        encoding="utf-8",
    )
    settings = Settings(
        news_html=news_html,
        database_path=tmp_path / "agent.sqlite3",
        output_dir=tmp_path / "drafts",
    )

    first = run(settings)
    second = run(settings)

    assert len(first["saved_paths"]) == 1
    assert Path(first["saved_paths"][0]).exists()
    assert second["saved_paths"] == []
