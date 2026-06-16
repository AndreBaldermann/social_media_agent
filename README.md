# Social Media Agent

Lokaler, mechanischer Workflow für technische Social-Media-Assets aus einem GitHub-Repository.

Der Agent nutzt **kein OpenAI und kein Claude**. Die Generierung läuft lokal über **Ollama** mit `qwen3-coder-next:latest` als Default-Modell und einem Kontextfenster von `128000` Tokens. Ein anderes lokales Ollama-Modell kann per CLI angegeben werden.

## Flow

1. Du übergibst einen Link zu einem GitHub-Repository.
2. Das Repository wird lokal geklont.
3. Der Agent baut einen kompakten Repository-Snapshot aus Dateibaum und wichtigen Textdateien.
4. Ollama erzeugt eine technische HTML-Analyse des Repositories.
   - technische Details,
   - Architektur und erkennbare Module,
   - business-ready Aspekte,
   - die 3 größten Verbesserungen.
5. Aus dem HTML-Report erzeugt Ollama einen LinkedIn-Artikel als Plain Text mit Emojis.
6. Aus dem HTML-Report erzeugt Ollama einen kurzen X/Twitter-Post oder Thread.
7. Aus dem HTML-Report erzeugt Ollama einen kurzen Bluesky-Post oder Thread.
8. Alle Dateien werden lokal gespeichert.

## Voraussetzungen

```bash
ollama pull qwen3-coder-next:latest
```

Optional für Entwicklung:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Nutzung

```bash
social-media-agent https://github.com/org/repo
```

Mit Optionen:

```bash
social-media-agent https://github.com/org/repo \
  --workspace-dir workspace/repos \
  --out output \
  --model qwen3-coder-next:latest \
  --ctx 128000 \
  --force
```

## Outputs

Pro Repository entsteht ein Ordner unter `output/` mit:

- `repo-report.html` — technische HTML-Analyse,
- `linkedin.txt` — LinkedIn-Artikel als eine Plain-Text-Zeile,
- `x.txt` — kurzer X/Twitter-Post oder Thread als eine Plain-Text-Zeile,
- `bluesky.txt` — kurzer Bluesky-Post oder Thread als eine Plain-Text-Zeile.

## Projektstruktur

- `src/social_media_agent/repository.py` — klont das Repo und baut den Snapshot.
- `src/social_media_agent/generator.py` — ruft lokal die Ollama-API auf und erzeugt die Inhalte.
- `src/social_media_agent/writer.py` — schreibt HTML- und TXT-Dateien.
- `src/social_media_agent/workflow.py` — verbindet Clone, Snapshot, Ollama und Output.
- `src/social_media_agent/cli.py` — CLI für GitHub-Link, Modell, Kontextfenster und Ausgabepfade.
