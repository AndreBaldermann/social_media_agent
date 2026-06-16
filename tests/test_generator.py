from social_media_agent.generator import OllamaClient, generate_assets
from social_media_agent.models import RepositorySnapshot


class FakeClient(OllamaClient):
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if len(self.prompts) == 1:
            return "<html><body><h1>Report</h1></body></html>"
        return "Text\nmit\nZeilen"


def test_generate_assets_calls_ollama_in_required_order(tmp_path) -> None:
    snapshot = RepositorySnapshot(
        repo_url="https://github.com/acme/repo",
        clone_dir=tmp_path,
        file_tree="README.md",
        selected_files=[("README.md", "# Demo")],
    )
    client = FakeClient()

    assets = generate_assets(snapshot, client)

    assert assets.html_report.startswith("<html>")
    assert assets.linkedin_text == "Text mit Zeilen"
    assert assets.x_text == "Text mit Zeilen"
    assert assets.bluesky_text == "Text mit Zeilen"
    assert "Aufgabe 1" in client.prompts[0]
    assert "LinkedIn" in client.prompts[1]
    assert "x.com" in client.prompts[2]
    assert "Bluesky" in client.prompts[3]
