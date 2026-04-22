
import os
import subprocess
import getpass
import time
import readline #type: ignore
import traceback
import sys

from pytuichat.inbox import *
from pytuichat.filereader import *
from pytuichat.lang import *
from pytuichat.socketio import singleCliCommand
from pytuichat.settings import SettingsManager as sm

def ping() -> bool:
    """
    Returns true if able to ping the socket for the inbox
    """
    # Connect to the contacts server if possible
    try:
        singleCliCommand(None, IDIOT(IDIOT_TYPE.PING, ""))

        return True
    except Exception:
        return False

def start() -> socket.socket:
    if ping():
        return createCliClient()
    else:
        print("Inbox starting")
        subprocess.Popen(
            [sys.executable, os.path.dirname(__file__) + "/dev_entrypoint.py", "--runInbox"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            preexec_fn=os.setsid,
            close_fds=True,
        )
        time.sleep(1)
        return createCliClient()

def stop(client: socket.socket) -> bool:
    """
    Returns true if able to ping the socket for the inbox
    """
    try:
        sendSocketIO(client, IDIOT(IDIOT_TYPE.STOP, "").toString())
        client.close()
        return True
    except Exception:
        return False

def _formatChats(chats: list[Chat]) -> str:
    """
    Given a list of chats, format them to look good in the CLI.
    """
    s: str = ""
    for c in chats:
        s += f"{c.getDisplayUniqueID()} - {c.getNumUnread()}\n"
    return s

def listChats(client: socket.socket) -> list[Chat]:
    """
    Returns a list of chats and info about the chats.
    """
    response: IDIOT = singleCliCommand(client, IDIOT(IDIOT_TYPE.LIST_CHATS, ""))
    return [Chat.fromJsonObj(t) for t in json.loads(response.data)]

def _formatMessage(msg: Message) -> str:
    """
    Formats a given message into a readable string.
    """
    mStatus: str = ""
    match msg.getStatus():
        case MessageStatus.SENDING:
            mStatus = getString("mrkSending")
        case MessageStatus.SENT:
            mStatus = getString("mrkSent")
        case MessageStatus.TIMEOUT:
            mStatus = getString("mrkTimout")
        case MessageStatus.UNREAD:
            mStatus = getString("mrkUnread")
        case MessageStatus.READ:
            mStatus = getString("mrkRead")
    strTime: str
    if sm.getSettingsManager().get24Hour():
        strTime: str = str(msg.getSent().strftime("%Y%m%d %H%M%p"))
    else:
        strTime: str = str(msg.getSent().strftime("%Y%m%d %I%M%p"))

    return f"{mStatus} {strTime} {msg.getSender()}: {msg.getContent()}"

def showSettings() -> dict[str, bool]:
    """
    Return a dict representing the user settings.
    """
    manager = sm.getSettingsManager()
    output: dict[str, bool] = {}
    output["24_hour_time"] = manager.get24Hour()
    output["show_nicknames"] = manager.getShowNicknames()
    return output

def updateNicks(showNicks: bool):
    """
    Update the settings manager and user's settings file with new preference.
    """
    manager = sm.getSettingsManager()
    manager.setShowNicknames(showNicks)

def updateTwentyFour(twentyfour: bool):
    """
    Update the settings manager and user's settings file with new preference.
    """
    manager = sm.getSettingsManager()
    manager.set24Hour(twentyfour)

def getMsgs(client: socket.socket, id: str, n: int = 100) -> str:
    """
    TODO
    """
    if not ping():
        return getString("errNotStarted")

    id = Chat.encodeParticipantID(Chat.decodeParticipantID(id) + [getpass.getuser()])
    
    response: IDIOT = singleCliCommand(client, IDIOT(IDIOT_TYPE.READ_MSGS, json.dumps({"id": id, "n": n})))
    
    msgStr: str = ""
    for m in json.loads(response.data):
        msgStr += _formatMessage(Message.fromJsonObj(m)) + "\n"
    return msgStr

def sendMsg(client: socket.socket, id: str, msg: str) -> str:
    """
    TODO
    """
    if not ping():
        return getString("errNotStarted")
    
    id = Chat.encodeParticipantID(Chat.decodeParticipantID(id) + [getpass.getuser()])
    dm: DeliveryMessage = DeliveryMessage(
        Message(
            msg,
            getpass.getuser(),
        ),
        Chat.decodeParticipantID(id),
        id
    )
    response: IDIOT = singleCliCommand(client, IDIOT(IDIOT_TYPE.SEND_MSG, json.dumps(dm.toJsonObj())))

    return response.data

def createChat(client: socket.socket, inp: str) -> str:
    chatid: str = Chat.encodeParticipantID("".join(inp.split()).split(","))
    return singleCliCommand(client, IDIOT(IDIOT_TYPE.CREATE_CHAT, chatid)).data

def runcli(args: list[str]) -> None:
    """
    Runs once for the CLI. This handles CLI commands from the user.
    """
    setLangMap("en_us")
    client: socket.socket
    client = start()

    # Initiate variables
    running: bool = True
    inp: list[str]

    # If there are cli args, running in singular mode. Prompt the user as to
    # the app running in singular or interactive mode.
    cliArgs: bool = len(args) > 0
    if not cliArgs:
        print(getString("pptInteractive"))
    else:
        print(getString("pptSingular"))
    
    # Start the running loop
    while running:
        # If running singular, this is the only time the loop will run
        if cliArgs:
            inp = args
            running = False
        else:
            inp = input(getString("pptConsole")).split(" ")
        
        # Handle the given command
        try:
            match inp[0]:
                # Handle no command
                case "":
                    continue

                # Handle help command
                case "help":
                    print("TODO console help")
                
                # Handle exit command
                case "exit":
                    print(getString("pptExiting"))
                    running = False
                    continue

                case "start":
                    cl = start()
                    if client:
                        client.close()
                        client = cl
                        print("Inbox has started")
                    else:
                        print("Inbox failed to start")
                case "ping":
                    if ping():
                        print("Inbox is running")
                    else:
                        print("Inbox is NOT running")
                case "stop":
                    stop(client)
                    print("Inbox has stopped")
                case "ls" | "list":
                    chats = listChats(client)
                    print(_formatChats(chats))
                case "read":
                    chat = getMsgs(client, inp[1], int(inp[2] if len(inp) >= 3 else 10))
                    print(chat)
                case "send":
                    tf = sendMsg(client, inp[1], inp[2])
                    print("Message send:", tf)
                case "create":
                    print(createChat(client, inp[1]))
                case "settings":
                    if len(inp) == 1:
                        print(showSettings())
                    elif len(inp) != 3:
                        print("TODO HELP STRING SETTINGS")
                    elif inp[1] == "24hour" and inp[2] in ["true", "false"]:
                        print("Updating 24_hour_time")
                        updateTwentyFour(inp[2] == "true")
                    elif inp[1] == "nicks" and inp[2] in ["true", "false"]:
                        print("Updating show_nicknames")
                        updateNicks(inp[2] == "true")
                    else:
                        print("TODO HELP STRING SETTINGS")
                case "tmp":
                    sendSocketIO(client, IDIOT(IDIOT_TYPE.PING, "").toString())
                    print(recieveSocketIO(client))
                    sendSocketIO(client, IDIOT(IDIOT_TYPE.PING, "").toString())
                    print(recieveSocketIO(client))
                case _:
                    print(getString("pptUnknown") + inp[0])
            
            # Add a line for spacing
            print(getString("pptEndReq"))
            print()
        except Exception as e:
            print(e)
            print(traceback.format_exc())