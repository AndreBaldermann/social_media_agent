from social_media_agent.generator import generate_draft
from social_media_agent.models import Article


def test_generate_draft_uses_fallback_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    article = Article(
        title="Testartikel",
        url="https://example.com/test",
        content="Dies ist ein kurzer Inhalt.",
        source_hash="abc",
    )

    draft = generate_draft(article, model="unused")

    assert "Testartikel" in draft.linkedin
    assert "https://example.com/test" in draft.twitter
    assert draft.bluesky
