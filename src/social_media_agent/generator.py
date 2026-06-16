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
Du bist ein technischer Repository-Analyst und arbeitest ausschließlich lokal.
Analysiere das folgende GitHub-Repository anhand des bereitgestellten Snapshots.

Aufgabe 1: Erzeuge eine vollständige HTML-Datei.
Regeln:
- Antworte ausschließlich mit HTML-Code, ohne Markdown-Codefence.
- Schreibe auf Deutsch.
- Beschreibe technisch detailliert, was das Repository macht.
- Erkläre Architektur, zentrale Module, Datenflüsse, APIs/CLIs und Tests, sofern erkennbar.
- Gehe konkret darauf ein, welche Aspekte besonders business-ready sind.
- Nenne die 3 größten Verbesserungen als priorisierte Liste.
- Wenn Informationen nicht im Snapshot enthalten sind, markiere sie als nicht erkennbar.

Repository-Snapshot:
{repo_context}
""".strip()


def _linkedin_prompt(html_report: str) -> str:
    return f"""
Du bekommst einen technischen HTML-Report über ein Repository.
Schreibe daraus einen LinkedIn-Artikel auf Deutsch.
Regeln:
- Plain text, kein Markdown, kein HTML.
- Keine Zeilenumbrüche; alles in einer einzigen Zeile.
- Nutze passende Emojis.
- Hebe besonders business-ready Aspekte hervor.
- Nenne kurz die 3 wichtigsten Verbesserungen.
- Kein erfundener Inhalt.

HTML-Report:
{html_report}
""".strip()


def _x_prompt(html_report: str) -> str:
    return f"""
Du bekommst einen technischen HTML-Report über ein Repository.
Schreibe einen kurzen Tweet oder Thread für x.com auf Deutsch.
Regeln:
- Plain text, kein Markdown, kein HTML.
- Keine Zeilenumbrüche; trenne mehrere Tweets mit " || ".
- Kurz halten.
- Fokus: was ist business-ready und welche 1-3 Verbesserungen sind am wichtigsten?
- Kein erfundener Inhalt.

HTML-Report:
{html_report}
""".strip()


def _bluesky_prompt(html_report: str) -> str:
    return f"""
Du bekommst einen technischen HTML-Report über ein Repository.
Schreibe einen kurzen Bluesky-Post oder Thread auf Deutsch.
Regeln:
- Plain text, kein Markdown, kein HTML.
- Keine Zeilenumbrüche; trenne mehrere Posts mit " || ".
- Kurz halten.
- Fokus: business-ready Aspekte und wichtigste Verbesserungen.
- Kein erfundener Inhalt.

HTML-Report:
{html_report}
""".strip()


def _single_line(value: str) -> str:
    return " ".join(value.replace("\r", " ").replace("\n", " ").split())
