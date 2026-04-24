from typing import cast
import time
import threading

from textual.app import App, ComposeResult
from textual.widgets import Input, TextArea, Button, Footer, Header, Label
from textual.containers import Vertical
from textual.screen import Screen
from textual.binding import Binding

from pytuichat.lang import *
from pytuichat import cli
from pytuichat.chat import Chat
from pytuichat.socketio import *

setLangMap("en_us")

class _tui:
    activeChat: str = ""
    app: App[None]
    client: socket.socket
    running: bool
    ut: threading.Thread

class ErrorMsgScreen(Screen[None]):
    def __init__(self, msg: str):
        self.msg = msg
    def compose(self) -> ComposeResult:
        yield Label(self.msg)

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
        chts: list[Chat] = cli.listChats(_tui.client)
        self.vertical: Vertical = Vertical(*[
                Button(
                    f"{c.getUniqueID()} - {c.getNumUnread()}🔔",
                    name=c.getUniqueID(),
                    classes="chatbtn",
                    compact=True,
                )
                for c in chts
            ])
        yield self.vertical
        yield Footer()
        self.refresh(layout=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle when the button is pressed. On this page, thats a chat button.
        """
        if "chatbtn" in event.button.classes:
            _tui.activeChat = cast(str, event.button.name)
            _tui.app.push_screen(MessageScreen())



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
        yield Label(getString("lblCreateNewChat"))
        yield Input(placeholder="Type something here...", id="input")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle input when the user presses Enter.
        """
        inp: str = "".join(event.input.value.split())
        if not inp:
            return

        chatid = cli.createChat(_tui.client, inp)
        event.input.value = ""
        _tui.activeChat = chatid
        _tui.app.pop_screen()
        _tui.app.push_screen(MessageScreen())

class MessageScreen(Screen[None]):
    """
    The screen where you view and send messages.
    """

    CSS = """
    #label { width: 100%; text-align: center; }
    """

    def compose(self) -> ComposeResult:
        """
        Compose the page.
        """
        yield Header()
        yield Label("<<< " + _tui.activeChat + " >>>", id="label")
        self.content: TextArea = TextArea("", id="content", read_only=True)
        yield self.content
        yield Input(placeholder="Type something here...", id="input")
        yield Footer()

        self.updateMessages()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handle input when the user presses Enter.
        """
        cli.sendMsg(_tui.client, _tui.activeChat, event.input.value)
        event.input.value = ""
        self.updateMessages()

    def updateMessages(self) -> None:
        self.content.text = cli.getMsgs(_tui.client, _tui.activeChat)

class HelpScreen(Screen[None]):
    """
    The screen that shows help for the app.
    """

    def compose(self) -> ComposeResult:
        """
        Compose the page.
        """
        yield Header()
        yield TextArea(getString("txtHelpTui"), read_only=True)
        yield Footer()

class SettingsScreen(Screen[None]):
    """
    The screen that allows the user to view and change their settings.
    """
    
    CSS = """
    #label { width: 100%; text-align: center; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Options")
        options: dict[str, bool] = cli.showSettings()
        yield Vertical(
            *[
                Button(
                    f"{k}: {"On" if options.get(k) else "Off"}",
                    name=k,
                    classes="setbtn",
                    compact=True,
                )
            for k in options.keys()
            ]
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.name == "show_nicknames":
            option = False if cli.showSettings()["show_nicknames"] else True
            cli.updateNicks(option)
            if option:
                event.button.label = "show_nicknames: On"
            else:
                event.button.label = "show_nicknames: Off"
        elif event.button.name == "24_hour_time":
            option = False if cli.showSettings()["24_hour_time"] else True
            cli.updateTwentyFour(option)
            if option:
                event.button.label = "24_hour_time: On"
            else:
                event.button.label = "24_hour_time: Off"

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
        Binding("ctrl+o", "options", "Options", show=True),
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
    
    async def action_quit(self) -> None:
        """
        Quit the app.
        """
        _tui.client.close()
        _tui.running = False
        return await super().action_quit()

    async def action_kill(self) -> None:
        # return await super().action_quit()
        cli.stop(_tui.client)
        return await self.action_quit()
    
    async def action_newc(self) -> None:
        if type(self.screen_stack[-1]) == DashboardScreen:
            self.push_screen(NewChatScreen())
    
    async def action_options(self) -> None:
        if type(self.screen_stack[-1]) == DashboardScreen:
            self.push_screen(SettingsScreen())  

    def on_mount(self) -> None:
        # self.switch_mode("dashboard")
        self.title = getString("lblTitle")
        self.sub_title = getString("lblSubTitle")
        
        self.switch_mode("loading")

        _tui.client = cli.start()
        _tui.running = True
        _tui.ut.start()
        self.switch_mode("dashboard")

def runtui() -> None:
    """
    Run the TUI version of the app.
    """
    _tui.app = ModesApp()
    _tui.ut = threading.Thread(target=checkUpdates)
    _tui.app.run()

def checkUpdates() -> None:
    """
    While true, check for updates sent by the inbox.
    """
    try:
        while _tui.running:
            time.sleep(0.1)
            if hasData(_tui.client):
                data: str = IDIOT.fromString(recieveSocketIO(_tui.client)).data
                print(data)
                if type(_tui.app.screen_stack[-1]) == DashboardScreen:
                    _tui.app.screen_stack[-1].compose()
                elif type(_tui.app.screen_stack[-1]) == MessageScreen:
                    if data == _tui.activeChat:
                        _tui.app.screen_stack[-1].updateMessages()
                with open("./tmpfile", "a") as f:
                    f.write(data)
    except Exception as e:
        with open("./tmpfile", "a") as f:
            f.write(str(e))