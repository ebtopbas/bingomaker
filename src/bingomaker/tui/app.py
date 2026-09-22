from __future__ import annotations

import json
from functools import partial
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Static, Switch

from ..config import BingoConfig, safe_path_component
from ..generator import BingoBoardGenerator
from ..visualizer import BingoBoardPdf
from .widgets import EditableListPanel, PathPromptScreen


class BingoMakerApp(App[None]):
    TITLE = "Bingo Maker"

    CSS = """
    #board-info {
        height: auto;
        padding: 1 2;
    }

    #board-info Input {
        margin-right: 1;
    }

    #name {
        width: 1fr;
    }

    #free-space-switch {
        margin-right: 1;
    }

    #free-space-text {
        width: 1fr;
    }

    #lists {
        height: 1fr;
    }

    EditableListPanel {
        width: 1fr;
        height: 1fr;
        border: round $primary;
        padding: 1;
        margin: 0 1;
    }

    EditableListPanel #items {
        height: 1fr;
        border: round $surface;
    }

    .add-row {
        height: auto;
    }

    .add-row Input {
        width: 1fr;
    }

    #generate-bar {
        height: auto;
        padding: 1 2;
    }

    #generate-bar Input {
        width: 1fr;
        margin-right: 1;
    }

    #status {
        height: auto;
        padding: 0 2 1 2;
    }
    """

    def __init__(self, config_path: Path | None = None) -> None:
        super().__init__()
        self._initial_config_path = config_path

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="root"):
            with Horizontal(id="board-info"):
                yield Input(placeholder="Board name", id="name")
                yield Switch(id="free-space-switch")
                yield Input(
                    placeholder="Free space text",
                    id="free-space-text",
                    disabled=True,
                )
            with Horizontal(id="lists"):
                yield EditableListPanel(
                    "Sentences", placeholder="Add a sentence...", id="sentences-panel"
                )
                yield EditableListPanel(
                    "People", placeholder="Add a person...", id="people-panel"
                )
            with Horizontal(id="generate-bar"):
                yield Input(value="output", placeholder="Output dir", id="output-dir")
                yield Input(placeholder="Seed (optional)", id="seed")
                yield Button("Load config", id="load")
                yield Button("Save config", id="save")
                yield Button(
                    "Generate PDFs", id="generate", variant="success", disabled=True
                )
            yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        if self._initial_config_path is not None:
            self._load_config_file(str(self._initial_config_path))
        else:
            self._revalidate()
        self.query_one("#name", Input).focus()

    @on(Switch.Changed, "#free-space-switch")
    def _free_space_toggled(self, event: Switch.Changed) -> None:
        self.query_one("#free-space-text", Input).disabled = not event.value
        self._revalidate()

    @on(Input.Changed, "#name")
    @on(Input.Changed, "#free-space-text")
    def _field_changed(self) -> None:
        self._revalidate()

    @on(EditableListPanel.Changed)
    def _list_changed(self) -> None:
        self._revalidate()

    def _current_config(self) -> BingoConfig:
        name = self.query_one("#name", Input).value.strip()
        free_space_enabled = self.query_one("#free-space-switch", Switch).value
        free_space_text = self.query_one("#free-space-text", Input).value.strip()
        free_space = free_space_text if free_space_enabled else None
        sentences = self.query_one("#sentences-panel", EditableListPanel).items
        people = self.query_one("#people-panel", EditableListPanel).items

        return BingoConfig(name, free_space, sentences, people)

    def _revalidate(self) -> BingoConfig | None:
        status = self.query_one("#status", Static)
        generate_button = self.query_one("#generate", Button)

        try:
            config = self._current_config()
        except (ValueError, TypeError) as exc:
            status.update(f"[red]{exc}[/red]")
            generate_button.disabled = True
            return None

        rows, cols = config.dimensions
        status.update(
            f"[green]{rows}x{cols} board - "
            f"ready to generate for {len(config.people)} people.[/green]"
        )
        generate_button.disabled = False
        return config

    @on(Button.Pressed, "#load")
    def _load_pressed(self) -> None:
        self.push_screen(
            PathPromptScreen(
                "Load config",
                "Path to JSON config",
                default=str(self._initial_config_path or ""),
            ),
            self._load_config_file,
        )

    @on(Button.Pressed, "#save")
    def _save_pressed(self) -> None:
        self.push_screen(
            PathPromptScreen(
                "Save config", "Path to save JSON config", default="config.json"
            ),
            self._save_config_file,
        )

    def _load_config_file(self, path_str: str | None) -> None:
        if not path_str:
            return

        path = Path(path_str)

        try:
            config = BingoConfig.from_json(path)
        except (ValueError, TypeError, OSError) as exc:
            self.notify(f"Could not load {path}: {exc}", severity="error")
            return

        self.query_one("#name", Input).value = config.name

        has_free_space = config.free_space is not None
        self.query_one("#free-space-switch", Switch).value = has_free_space

        free_space_text = self.query_one("#free-space-text", Input)
        free_space_text.value = config.free_space or ""
        free_space_text.disabled = not has_free_space

        self.query_one("#sentences-panel", EditableListPanel).set_items(
            config.sentences
        )
        self.query_one("#people-panel", EditableListPanel).set_items(config.people)

        self._revalidate()
        self.notify(f"Loaded {path}")

    def _save_config_file(self, path_str: str | None) -> None:
        if not path_str:
            return

        config = self._revalidate()
        if config is None:
            self.notify("Fix validation errors before saving.", severity="error")
            return

        path = Path(path_str)
        data = {
            "name": config.name,
            "free_space": config.free_space,
            "sentences": config.sentences,
            "people": config.people,
        }

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            self.notify(f"Could not save {path}: {exc}", severity="error")
            return

        self.notify(f"Saved {path}")

    @on(Button.Pressed, "#generate")
    def _generate_pressed(self) -> None:
        config = self._revalidate()
        if config is None:
            self.notify("Fix validation errors before generating.", severity="error")
            return

        output_dir = Path(
            self.query_one("#output-dir", Input).value.strip() or "output"
        )
        seed_text = self.query_one("#seed", Input).value.strip()

        try:
            seed = int(seed_text) if seed_text else None
        except ValueError:
            self.notify("Seed must be an integer.", severity="error")
            return

        generate_button = self.query_one("#generate", Button)
        generate_button.disabled = True

        self.run_worker(
            partial(self._generate, config, output_dir, seed, generate_button),
            thread=True,
            exclusive=True,
        )

    def _generate(
        self,
        config: BingoConfig,
        output_dir: Path,
        seed: int | None,
        generate_button: Button,
    ) -> None:
        try:
            generator = BingoBoardGenerator(config, seed=seed)
            renderer = BingoBoardPdf(config.name, config.free_space is not None)
            boards = generator.generate(len(config.people))

            board_dir = output_dir / safe_path_component(config.name)

            for name, board in zip(config.people, boards, strict=True):
                renderer.render(
                    board=board,
                    name=name,
                    output_path=board_dir / f"{safe_path_component(name)}.pdf",
                )
        except (ValueError, OSError) as exc:
            self.call_from_thread(self.notify, str(exc), severity="error")
            return
        finally:
            self.call_from_thread(setattr, generate_button, "disabled", False)

        self.call_from_thread(
            self.notify, f"Generated {len(config.people)} board(s) in {board_dir}"
        )
