"""LangGraph workflow for the mechanical social-media draft flow."""

from __future__ import annotations

import importlib.util
from typing import TypedDict

from social_media_agent.config import Settings
from social_media_agent.generator import generate_draft
from social_media_agent.html_reader import candidates_to_articles, read_candidates
from social_media_agent.markdown import write_draft
from social_media_agent.models import Article, SocialDraft
from social_media_agent.storage import ArticleStore

_HAS_LANGGRAPH = importlib.util.find_spec("langgraph") is not None
if _HAS_LANGGRAPH:
    from langgraph.graph import END, StateGraph


class WorkflowState(TypedDict):
    """State passed between workflow nodes."""

    settings: Settings
    articles: list[Article]
    drafts: list[SocialDraft]
    saved_paths: list[str]


def build_graph():
    """Build the LangGraph state machine, or a local equivalent when dependencies are absent."""

    if not _HAS_LANGGRAPH:
        return _SequentialGraph()

    graph = StateGraph(WorkflowState)
    graph.add_node("read_news_html", _read_news_html)
    graph.add_node("detect_new_articles", _detect_new_articles)
    graph.add_node("generate_posts", _generate_posts)
    graph.add_node("save_markdown", _save_markdown)

    graph.set_entry_point("read_news_html")
    graph.add_edge("read_news_html", "detect_new_articles")
    graph.add_edge("detect_new_articles", "generate_posts")
    graph.add_edge("generate_posts", "save_markdown")
    graph.add_edge("save_markdown", END)
    return graph.compile()


def run(settings: Settings) -> WorkflowState:
    """Run the full article-to-drafts workflow."""

    initial_state: WorkflowState = {
        "settings": settings,
        "articles": [],
        "drafts": [],
        "saved_paths": [],
    }
    return build_graph().invoke(initial_state)


def _read_news_html(state: WorkflowState) -> WorkflowState:
    settings = state["settings"]
    candidates = read_candidates(settings.news_html)
    return {**state, "articles": candidates_to_articles(candidates)}


def _detect_new_articles(state: WorkflowState) -> WorkflowState:
    store = ArticleStore(state["settings"].database_path)
    new_articles = [
        article for article in state["articles"] if not store.has_article(article.source_hash)
    ]
    return {**state, "articles": new_articles}


def _generate_posts(state: WorkflowState) -> WorkflowState:
    settings = state["settings"]
    drafts = [generate_draft(article, settings.model) for article in state["articles"]]
    return {**state, "drafts": drafts}


def _save_markdown(state: WorkflowState) -> WorkflowState:
    settings = state["settings"]
    store = ArticleStore(settings.database_path)
    saved_paths: list[str] = []
    for draft in state["drafts"]:
        path = write_draft(draft, settings.output_dir)
        saved_paths.append(str(path))
        if not settings.dry_run:
            store.remember(draft.article, path)
    return {**state, "saved_paths": saved_paths}


class _SequentialGraph:
    """Dependency-light stand-in that preserves the same invoke contract for local tests."""

    def invoke(self, state: WorkflowState) -> WorkflowState:
        for node in (_read_news_html, _detect_new_articles, _generate_posts, _save_markdown):
            state = node(state)
        return state
