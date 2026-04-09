from textual.app import App, ComposeResult
from textual.widgets import Label, Input, TextArea, Button, Footer, Header
from textual.containers import Horizontal
from textual.screen import Screen

import lang
import cli

lang.setLangMap("en_us")

EXAMPLE_MARKDOWN = """\
# Markdown Viewer

This is an example of Textual's `MarkdownViewer` widget.


## Features

Markdown syntax and extensions are supported.

- Typography *emphasis*, **strong**, `inline code` etc.
- Headers
- Lists (bullet and ordered)
- Syntax highlighted code blocks
- Tables!

## Tables

Tables are displayed in a DataTable widget.

| Name            | Type   | Default | Description                        |
| --------------- | ------ | ------- | ---------------------------------- |
| `show_header`   | `bool` | `True`  | Show the table header              |
| `fixed_rows`    | `int`  | `0`     | Number of fixed rows               |
| `fixed_columns` | `int`  | `0`     | Number of fixed columns            |
| `zebra_stripes` | `bool` | `False` | Display alternating colors on rows |
| `header_height` | `int`  | `1`     | Height of header row               |
| `show_cursor`   | `bool` | `True`  | Show a cell cursor                 |


## Code Blocks

Code blocks are syntax highlighted.

```python
class ListViewExample(App):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )
        yield Footer()
```

## Litany Against Fear

I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain.
"""

class DashboardScreen(Screen):
    """
    The home screen when the app launches. Allows navigation to chats, help
    pages, and settings.
    """

    def compose(self) -> ComposeResult:
        """
        Compose the page.
        """
        yield Header()
        yield Horizontal(
            Button(lang.getString("btnExit"), compact=True, id="btnExit"),
            Label(lang.getString("lblTitle")),
            id="nav"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btnExit":
            self.exit(str(event.button))

class MessageScreen(Screen):

    def compose(self) -> ComposeResult:
        """
        Compose the page.
        """
        yield Horizontal(
            Button(lang.getString("btnBack"), compact=True),
            Button(lang.getString("btnExit"), compact=True, id="btnExit"),
            id="nav"
        )
        yield TextArea(cli.getMsgs("kittkat", 10), id="content", read_only=True)
        yield Input(placeholder="Type something here...", id="input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input when the user presses Enter."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btnExit":
            """
            """

class HelpScreen(Screen):
    """
    The screen that shows help for the app.
    """

    def compose(self) -> ComposeResult:
        """
        Compose the page.
        """
        yield Header()
        yield TextArea(lang.getString("txtHelp"), read_only=True)
        yield Footer()


class ModesApp(App[None]):
    """
    The main application, which launches other screens.
    """

    CSS = """
    Screen { align: center middle; }
    #nav { height: auto; }
    """

    BINDINGS = [
        ("d", "switch_mode('dashboard')", "Dashboard"),
        ("s", "switch_mode('settings')", "Settings"),
        ("h", "switch_mode('help')", "Help"),
    ]

    MODES = { #type: ignore
        "dashboard": DashboardScreen,
        # "settings": SettingsScreen,
        "help": HelpScreen,
    }

    def on_mount(self) -> None:
        # self.switch_mode("dashboard")
        self.title = lang.getString("lblTitle")
        self.sub_title = lang.getString("lblSubTitle")
        self.push_screen(DashboardScreen())

if __name__ == "__main__":
    app = ModesApp()
    app.run()