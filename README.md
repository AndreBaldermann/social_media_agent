# Social Media Agent

A local, mechanical workflow for generating technical social media assets from a GitHub repository.

The agent uses **neither OpenAI nor Claude**. All content generation runs locally through **Ollama**, using `qwen3-coder-next:latest` as the default model and a context window of `128000` tokens. Any other local Ollama model can be specified via the CLI.

## Flow

1. Provide a GitHub repository URL.
2. The repository is cloned locally.
3. The agent builds a compact repository snapshot from the file tree and important text files.
4. Ollama generates a technical HTML analysis of the repository, including:

   * technical details,
   * architecture and identifiable modules,
   * business-ready aspects,
   * the 3 most important improvements.
5. Based on the HTML report, Ollama generates a LinkedIn article as plain text with emojis.
6. Based on the HTML report, Ollama generates a short X/Twitter post or thread.
7. Based on the HTML report, Ollama generates a short Bluesky post or thread.
8. All generated files are stored locally.

## Requirements

```bash
ollama pull qwen3-coder-next:latest
```

Optional for development:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Usage

```bash
social-media-agent https://github.com/org/repo
```

With additional options:

```bash
social-media-agent https://github.com/org/repo \
  --workspace-dir workspace/repos \
  --out output \
  --model qwen3-coder-next:latest \
  --ctx 128000 \
  --force
```

## Outputs

For each repository, a directory is created under `output/` containing:

* `repo-report.html` — technical HTML analysis
* `linkedin.txt` — LinkedIn article in plain text
* `x.txt` — short X/Twitter post or thread in plain text
* `bluesky.txt` — short Bluesky post or thread in plain text

## Project Structure

* `src/social_media_agent/repository.py` — clones the repository and builds the snapshot.
* `src/social_media_agent/generator.py` — calls the local Ollama API and generates content.
* `src/social_media_agent/writer.py` — writes HTML and text output files.
* `src/social_media_agent/workflow.py` — orchestrates cloning, snapshot generation, Ollama processing, and output creation.
* `src/social_media_agent/cli.py` — command-line interface for repository URLs, model selection, context window configuration, and output paths.
