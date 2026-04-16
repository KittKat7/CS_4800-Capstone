from typing import cast

from textual.app import App, ComposeResult
from textual.widgets import Input, TextArea, Button, Footer, Header, Label
from textual.containers import Vertical
from textual.screen import Screen
from textual.binding import Binding

import lang
import cli
from chat import Chat
from idiot import IDIOT, IDIOT_TYPE
import socketio

lang.setLangMap("en_us")

class _tui:
    activeChat: str = ""

class LoadingScreen(Screen[None]):
    """
    The home screen when the app launches. Allows navigation to chats, help
    pages, and settings.
    """

    def compose(self) -> ComposeResult:
        """
        Compose the page.
        """
        yield Header()
        yield Label("Page is loading!!! TODO")

class DashboardScreen(Screen[None]):
    """
    The home screen when the app launches. Allows navigation to chats, help
    pages, and settings.
    """

    CSS = """
    .chatbtn { width: 100%; text-align: left; content-align: left middle; }
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
                )
                for c in chts
            ]
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "chatbtn" in event.button.classes:
            _tui.activeChat = cast(str, event.button.name)
            app.push_screen(MessageScreen())

class NewChatScreen(Screen[None]):
    """
    The home screen when the app launches. Allows navigation to chats, help
    pages, and settings.
    """

    def compose(self) -> ComposeResult:
        """
        Compose the page.
        """
        yield Header()
        yield Label(lang.getString("lblCreateNewChat"))
        yield Input(placeholder="Type something here...", id="input")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle input when the user presses Enter.
        """
        inp: str = "".join(event.input.value.split())
        if not inp:
            return

        chatid: str = Chat.encodeParticipantID(inp.split(","))
        chatid = socketio.singleCliCommand(IDIOT(IDIOT_TYPE.CREATE_CHAT, chatid)).data
        event.input.value = ""
        _tui.activeChat = chatid
        app.pop_screen()
        app.push_screen(MessageScreen())
        # self.updateMessages()

class MessageScreen(Screen[None]):
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
        cli.sendMsg(_tui.activeChat, event.input.value)
        event.input.value = ""
        self.updateMessages()

    def updateMessages(self) -> None:
        self.content.text = cli.getMsgs(_tui.activeChat)

class HelpScreen(Screen[None]):
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
        Binding("ctrl+k", "kill", "Kill (inbox)", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+b", "back", "Back", show=True),
        Binding("ctrl+n", "newc", "New Chat", show=True),
        Binding("h", "help", "Help", show=True),
    ]

    MODES = { #type: ignore
        "dashboard": DashboardScreen,
        "loading"  : LoadingScreen,
    }

    async def action_help(self) -> None:
        if type(self.screen_stack[-1]) != HelpScreen:
            self.push_screen(HelpScreen())

    async def action_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()
    
    async def action_kill(self) -> None:
        # return await super().action_quit()
        cli.stop()
        return await super().action_quit()
    
    async def action_newc(self) -> None:
        if type(self.screen_stack[-1]) == DashboardScreen:
            self.push_screen(NewChatScreen())

    def on_mount(self) -> None:
        # self.switch_mode("dashboard")
        self.title = lang.getString("lblTitle")
        self.sub_title = lang.getString("lblSubTitle")
        
        self.switch_mode("loading")

        if cli.start():
            self.switch_mode("dashboard")

if __name__ == "__main__":
    app: App[None] = ModesApp()
    app.run()