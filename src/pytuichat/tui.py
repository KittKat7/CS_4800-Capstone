from typing import cast

from textual.app import App, ComposeResult
from textual.widgets import Label, Input, TextArea, Button, Footer, Header
from textual.containers import Horizontal, Vertical
from textual.screen import Screen

import lang
import cli
from chat import Chat

lang.setLangMap("en_us")

activeChat: str = ""

class DashboardScreen(Screen):
    """
    The home screen when the app launches. Allows navigation to chats, help
    pages, and settings.
    """

    CSS = """
    .chatbtn { width: 100%; text-align: left; }
    """

    def compose(self) -> ComposeResult:
        """
        Compose the page.
        """
        yield Header()
        chts: list[Chat] = cli.listChats()
        yield Vertical(
            *[
                Button(
                    f"{c.getUniqueID()} - {c.getNumUnread()}🔔",
                    name=c.getUniqueID(),
                    classes="chatbtn",
                    compact=True,
                    # action="push_screen(\"HelpScreen()\")",
                )
                for c in chts
            ]
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "chatbtn" in event.button.classes:
            global activeChat
            activeChat = cast(str, event.button.name)
            self.app.push_screen(MessageScreen())

class MessageScreen(Screen):
    """
    The screen where you view and send messages.
    """

    def compose(self) -> ComposeResult:
        """
        Compose the page.
        """
        yield Header()
        self.content: TextArea = TextArea("", id="content", read_only=True)
        yield self.content
        yield Input(placeholder="Type something here...", id="input")
        yield Footer()

        self.updateMessages()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle input when the user presses Enter.
        """
        cli.sendMsg(activeChat, event.input.value)
        event.input.value = ""
        self.updateMessages()

    def updateMessages(self) -> None:
        self.content.text = cli.getMsgs(activeChat)

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
        ("ctrl+q", "quit", "quit"),
        ("ctrl+b", "back", "Back"),
        ("d", "switch_mode('dashboard')", "Dashboard"),
        ("h", "switch_mode('help')", "Help"),
    ]

    MODES = { #type: ignore
        "dashboard": DashboardScreen,
        "help": HelpScreen,
    }

    async def action_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def on_mount(self) -> None:
        # self.switch_mode("dashboard")
        self.title = lang.getString("lblTitle")
        self.sub_title = lang.getString("lblSubTitle")
        self.switch_mode("dashboard")

if __name__ == "__main__":
    app = ModesApp()
    app.run()