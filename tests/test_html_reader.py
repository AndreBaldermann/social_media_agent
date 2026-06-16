from pathlib import Path

from social_media_agent.html_reader import candidates_to_articles, read_candidates


def test_read_candidates_extracts_links(tmp_path: Path) -> None:
    html = tmp_path / "news.html"
    html.write_text(
        """
        <html><head><base href="https://example.com"></head><body>
          <article><a href="/post">Mein Artikel</a><p>Eine kurze Zusammenfassung.</p></article>
        </body></html>
        """,
        encoding="utf-8",
    )

    candidates = read_candidates(html)

    assert len(candidates) == 1
    assert candidates[0].title == "Mein Artikel"
    assert candidates[0].url == "https://example.com/post"
    assert "Zusammenfassung" in candidates[0].summary


def test_candidates_to_articles_creates_stable_hashes() -> None:
    candidates = read_candidates(Path("examples/news.html"))
    first = candidates_to_articles(candidates)[0]
    second = candidates_to_articles(candidates)[0]

    assert first.source_hash == second.source_hash
    assert first.content
