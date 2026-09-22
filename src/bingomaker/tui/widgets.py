from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, ListItem, ListView


class EditableListPanel(Vertical):
    """A titled, editable list of strings (add via input, remove selected)."""

    class Changed(Message):
        def __init__(self, items: list[str]) -> None:
            self.items = items
            super().__init__()

    def __init__(
        self,
        title: str,
        *,
        placeholder: str,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._title = title
        self._placeholder = placeholder
        self.items: list[str] = []

    def compose(self) -> ComposeResult:
        yield Label(self._title, classes="panel-title")
        yield ListView(id="items")
        with Horizontal(classes="add-row"):
            yield Input(placeholder=self._placeholder, id="new-item")
            yield Button("Add", id="add")
        yield Button("Remove selected", id="remove", variant="error")

    def set_items(self, items: list[str]) -> None:
        self.items = list(items)
        list_view = self.query_one("#items", ListView)
        list_view.clear()
        list_view.extend(ListItem(Label(item)) for item in self.items)
        self.post_message(self.Changed(list(self.items)))

    @on(Button.Pressed, "#add")
    def _add_pressed(self) -> None:
        self._commit_new_item()

    @on(Input.Submitted, "#new-item")
    def _new_item_submitted(self) -> None:
        self._commit_new_item()

    def _commit_new_item(self) -> None:
        input_widget = self.query_one("#new-item", Input)
        value = input_widget.value.strip()
        input_widget.value = ""
        input_widget.focus()

        if not value or value in self.items:
            return

        self.items.append(value)
        self.query_one("#items", ListView).append(ListItem(Label(value)))
        self.post_message(self.Changed(list(self.items)))

    @on(Button.Pressed, "#remove")
    def _remove_pressed(self) -> None:
        list_view = self.query_one("#items", ListView)
        index = list_view.index

        if index is None:
            return

        del self.items[index]
        list_view.pop(index)
        self.post_message(self.Changed(list(self.items)))


class PathPromptScreen(ModalScreen[str | None]):
    """A small modal that asks the user for a filesystem path."""

    DEFAULT_CSS = """
    PathPromptScreen {
        align: center middle;
    }

    PathPromptScreen > Vertical {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    PathPromptScreen Input {
        margin-bottom: 1;
    }

    PathPromptScreen Horizontal {
        height: auto;
        align: right middle;
    }

    PathPromptScreen Button {
        margin-left: 1;
    }
    """

    def __init__(self, title: str, placeholder: str, default: str = "") -> None:
        super().__init__()
        self._title = title
        self._placeholder = placeholder
        self._default = default

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._title)
            yield Input(value=self._default, placeholder=self._placeholder, id="path")
            with Horizontal():
                yield Button("Cancel", id="cancel")
                yield Button("OK", id="ok", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#path", Input).focus()

    @on(Button.Pressed, "#ok")
    def _confirm(self) -> None:
        self.dismiss(self.query_one("#path", Input).value.strip() or None)

    @on(Button.Pressed, "#cancel")
    def _cancel(self) -> None:
        self.dismiss(None)

    @on(Input.Submitted, "#path")
    def _submitted(self) -> None:
        self._confirm()
