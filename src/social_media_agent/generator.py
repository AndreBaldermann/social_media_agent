"""Generate channel-specific social media drafts."""

from __future__ import annotations

import json
import os
import textwrap

from social_media_agent.models import Article, SocialDraft

SYSTEM_PROMPT = """Du bist ein präziser Social-Media-Redakteur.
Schreibe auf Deutsch, sachlich, ohne Clickbait und ohne erfundene Details.
Gib ausschließlich valides JSON mit den Keys linkedin, twitter und bluesky zurück.
"""


def generate_draft(article: Article, model: str) -> SocialDraft:
    """Generate one draft set via LLM or deterministic fallback."""

    if os.getenv("OPENAI_API_KEY"):
        return _generate_with_openai(article, model)
    return _generate_fallback(article)


def _generate_with_openai(article: Article, model: str) -> SocialDraft:
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model=model, temperature=0.4)
    response = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            (
                "user",
                "\n".join(
                    [
                        "Erstelle Social-Media-Entwürfe für diesen Artikel.",
                        "LinkedIn: 2-4 kurze Absätze plus klare Frage am Ende.",
                        "Twitter/X: maximal 260 Zeichen inklusive Link.",
                        "Bluesky: maximal 280 Zeichen inklusive Link.",
                        f"Titel: {article.title}",
                        f"URL: {article.url}",
                        f"Inhalt: {article.content}",
                    ]
                ),
            ),
        ]
    )
    payload = json.loads(str(response.content))
    return SocialDraft.create(
        article=article,
        linkedin=payload["linkedin"].strip(),
        twitter=payload["twitter"].strip(),
        bluesky=payload["bluesky"].strip(),
    )


def _generate_fallback(article: Article) -> SocialDraft:
    excerpt = textwrap.shorten(article.content, width=180, placeholder=" ...")
    linkedin = (
        f"{article.title}\n\n"
        f"Kurz zusammengefasst: {excerpt}\n\n"
        f"Was ist eure Einschätzung dazu?\n\n{article.url}"
    )
    twitter = textwrap.shorten(f"{article.title} — {article.url}", width=260, placeholder=" …")
    bluesky = textwrap.shorten(
        f"{article.title}\n\n{excerpt}\n{article.url}",
        width=280,
        placeholder=" …",
    )
    return SocialDraft.create(article=article, linkedin=linkedin, twitter=twitter, bluesky=bluesky)
