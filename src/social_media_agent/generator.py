"""Generate repository report and social posts with local Ollama."""

from __future__ import annotations

import json
import urllib.request

from social_media_agent.models import GeneratedAssets, RepositorySnapshot


class OllamaClient:
    """Small wrapper around the local Ollama CLI."""

    def __init__(self, model: str, context_window: int = 128_000) -> None:
        self.model = model
        self.context_window = context_window

    def generate(self, prompt: str) -> str:
        """Run a prompt against the local Ollama API and return the response."""

        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_ctx": self.context_window},
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=1800) as response:  # noqa: S310
            body = json.loads(response.read().decode("utf-8"))
        return str(body.get("response", "")).strip()


def generate_assets(snapshot: RepositorySnapshot, client: OllamaClient) -> GeneratedAssets:
    """Generate the HTML report and channel texts in the required order."""

    context = _render_repository_context(snapshot)
    html_report = client.generate(_html_prompt(context))
    linkedin_text = _single_line(client.generate(_linkedin_prompt(html_report)))
    x_text = _single_line(client.generate(_x_prompt(html_report)))
    bluesky_text = _single_line(client.generate(_bluesky_prompt(html_report)))
    return GeneratedAssets.create(
        html_report=html_report,
        linkedin_text=linkedin_text,
        x_text=x_text,
        bluesky_text=bluesky_text,
    )


def _render_repository_context(snapshot: RepositorySnapshot) -> str:
    file_sections = []
    for path, content in snapshot.selected_files:
        file_sections.append(f"--- FILE: {path} ---\n{content}")
    return "\n\n".join(
        [
            f"Repository URL: {snapshot.repo_url}",
            f"Local clone: {snapshot.clone_dir}",
            "File tree:",
            snapshot.file_tree,
            "Selected file contents:",
            "\n\n".join(file_sections),
        ]
    )


def _html_prompt(repo_context: str) -> str:
    return f"""
You are a technical repository analyst and work exclusively with local information.

Analyze the following GitHub repository based solely on the provided snapshot.

Task 1: Generate a complete HTML document.

Rules:
- Respond exclusively with HTML code, without any Markdown code fences.
- Write in English.
- Provide a technically detailed description of what the repository does.
- Explain the architecture, core modules, data flows, APIs/CLIs, and tests, if identifiable.
- Specifically address which aspects are particularly business-ready.
- List the 3 most important improvements as a prioritized list.
- If information is not contained in the snapshot, explicitly mark it as "nicht erkennbar" (not identifiable).

Repository Snapshot:
{repo_context}
""".strip()


def _linkedin_prompt(html_report: str) -> str:
    return f"""
You will receive a technical HTML report about a repository.

Write a professional LinkedIn article in English based on that report.

Rules:

* Plain text only; no Markdown and no HTML.
* Use short, readable paragraphs separated by blank lines.
* Start with a strong opening that explains what the repository does and why it matters. 
* After that, incldue a link to the the github repository.
* Highlight the most important business-ready aspects.
* Explain the key technical strengths in a concise and accessible way.
* Include a short section covering the 3 most important improvements, ordered by priority.
* End with a brief conclusion or takeaway.
* Use appropriate emojis, but do not overuse them.
* Do not invent any information.
* Only describe facts that can be derived from the HTML report.

HTML Report:
{html_report}
""".strip()


def _x_prompt(html_report: str) -> str:
    return f"""
You will receive a technical HTML report about a repository.

Write a short tweet or thread for X.com in English based on that report.

Rules:

* Plain text only; no Markdown and no HTML.
* Start with a strong opening that explains  why it matters. 
* * After that, incldue a link to the the github repository.
*  multiple tweets with " || "
* Keep it concise.
* Focus on what is business-ready and which 1–3 improvements are most important.
* Do not invent any information.

HTML Report:
{html_report}
""".strip()


def _bluesky_prompt(html_report: str) -> str:
    return f"""
You will receive a technical HTML report about a repository.

Write a short Bluesky post or thread in English based on that report.

Rules:

* Plain text only; no Markdown and no HTML.
* Start with a strong opening that explains  why it matters. 
* * After that, incldue a link to the the github repository.
* separate multiple posts with " || "
* Keep it concise.
* Focus on business-ready aspects and the most important improvements.
* Do not invent any information.

HTML Report:
{html_report}

""".strip()


def _single_line(value: str) -> str:
    #return " ".join(value.replace("\r", " ").replace("\n", " ").split())
    return value
