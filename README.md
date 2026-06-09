# Social Media Agent

Mechanischer Python/LangGraph-Workflow für wenige, manuell geprüfte Social-Media-Posts:

1. Script starten
2. `news.html` lesen
3. neue Artikel per SQLite erkennen
4. Inhalt aus HTML-Link/Artikelblock extrahieren
5. Entwürfe für LinkedIn, Twitter/X und Bluesky generieren
6. Markdown-Datei speichern
7. Entwürfe manuell prüfen
8. optional später manuell posten

Der Agent postet bewusst **nicht automatisch**.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Optional kann eine `.env` aus `.env.example` angelegt werden. Ohne `OPENAI_API_KEY` nutzt der Generator deterministische Template-Entwürfe; mit Key nutzt er `langchain-openai`.

## Schnellstart

```bash
social-media-agent init-db
social-media-agent run --news-html examples/news.html --out drafts
```

Die Markdown-Entwürfe landen standardmäßig in `drafts/`, die SQLite-Datenbank in `data/social_media_agent.sqlite3`.

## Wichtige Optionen

```bash
social-media-agent run \
  --news-html news.html \
  --db data/social_media_agent.sqlite3 \
  --out drafts \
  --model gpt-4.1-mini
```

- `--dry-run`: erstellt Markdown, merkt Artikel aber nicht als verarbeitet.
- `--model`: wird nur verwendet, wenn `OPENAI_API_KEY` gesetzt ist.

## Projektstruktur

- `src/social_media_agent/html_reader.py`: liest `news.html` und findet Artikelkandidaten.
- `src/social_media_agent/storage.py`: speichert verarbeitete Artikel in SQLite.
- `src/social_media_agent/generator.py`: generiert Social-Media-Entwürfe per LLM oder Fallback.
- `src/social_media_agent/markdown.py`: schreibt prüfbare Markdown-Dateien.
- `src/social_media_agent/workflow.py`: verbindet die Schritte als LangGraph-StateGraph.
- `src/social_media_agent/cli.py`: stellt `init-db` und `run` bereit.

## Nächste sinnvolle Ausbaustufen

- echten Artikelinhalt aus Ziel-URLs laden,
- Freigabe-Status in Markdown oder SQLite speichern,
- Qualitätschecks für Zeichenlimits und verbotene Claims ergänzen,
- erst danach optionale Posting-Adapter für LinkedIn, X/Twitter und Bluesky bauen.
