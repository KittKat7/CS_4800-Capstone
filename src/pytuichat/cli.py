
import sys
import os
import subprocess
import getpass
import time
import readline #type: ignore

from inbox import *
from filereader import *
import lang
from socketio import singleCliCommand
from settings import SettingsManager as sm

def ping() -> bool:
    """
    Returns true if able to ping the socket for the inbox
    """
    # Connect to the contacts server if possible
    try:
        socketio.singleCliCommand(IDIOT(IDIOT_TYPE.PING, ""))

        return True
    except Exception:
        return False

def start() -> bool:
    if ping():
        return True
    else:
        print("Inbox starting")
        subprocess.Popen(
            [sys.executable, "-c", "from inbox import Inbox; Inbox.runInbox()"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            preexec_fn=os.setsid,
            close_fds=True,
        )
        time.sleep(1)
        return ping()

def stop() -> bool:
    """
    Returns true if able to ping the socket for the inbox
    """
    try:
        client: socket.socket = socketio.createCliClient()
        socketio.sendSocketIO(client, IDIOT(IDIOT_TYPE.STOP, "").toString())
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
        s += f"{c.getUniqueID()} - {c.getNumUnread()}; "
    return s

def listChats() -> list[Chat]:
    """
    Returns a list of chats and info about the chats.
    """
    response: IDIOT = singleCliCommand(IDIOT(IDIOT_TYPE.LIST_CHATS, ""))
    return [Chat.fromJsonObj(t) for t in json.loads(response.data)]

def _formatMessage(msg: Message) -> str:
    """
    Formats a given message into a readable string.
    """
    mStatus: str = ""
    match msg.getStatus():
        case MessageStatus.SENDING:
            mStatus = lang.getString("mrkSending")
        case MessageStatus.SENT:
            mStatus = lang.getString("mrkSent")
        case MessageStatus.TIMEOUT:
            mStatus = lang.getString("mrkTimout")
        case MessageStatus.UNREAD:
            mStatus = lang.getString("mrkUnread")
        case MessageStatus.READ:
            mStatus = lang.getString("mrkRead")
    strTime: str
    if sm.getSettingsManager().get24Hour():
        strTime: str = str(msg.getSent().strftime("%Y%m%d %H%M%p"))
    else:
        strTime: str = str(msg.getSent().strftime("%Y%m%d %I%M%p"))

    return f"{mStatus} {strTime} {msg.getSender()}: {msg.getContent()}"

def getMsgs(id: str, n: int = 100) -> str:
    """
    TODO
    """
    if not ping():
        return lang.getString("errNotStarted")
    
    response: IDIOT = singleCliCommand(IDIOT(IDIOT_TYPE.READ_MSGS, json.dumps({"id": id, "n": n})))
    
    msgStr: str = ""
    for m in json.loads(response.data):
        msgStr += _formatMessage(Message.fromJsonObj(m)) + "\n"
    return msgStr

def sendMsg(chatid: str, msg: str) -> str:
    """
    TODO
    """
    if not ping():
        return lang.getString("errNotStarted")
    
    dm: DeliveryMessage = DeliveryMessage(
        Message(
            msg,
            getpass.getuser(),
        ),
        Chat.decodeParticipantID(chatid),
        chatid
    )
    response: IDIOT = singleCliCommand(IDIOT(IDIOT_TYPE.SEND_MSG, json.dumps(dm.toJsonObj())))

    return response.data

def runcli(args: list[str]) -> None:
    """
    Runs once for the CLI. This handles CLI commands from the user.
    """
    lang.setLangMap("en_us")

    # Initiate variables
    running: bool = True
    inp: list[str]

    # If there are cli args, running in singular mode. Prompt the user as to
    # the app running in singular or interactive mode.
    cliArgs: bool = len(args) > 0
    if not cliArgs:
        print(lang.getString("pptInteractive"))
    else:
        print(lang.getString("pptSingular"))
    
    # Start the running loop
    while running:
        # If running singular, this is the only time the loop will run
        if cliArgs:
            inp = args
            running = False
        else:
            inp = input(lang.getString("pptConsole")).split(" ")
        
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
                    print(lang.getString("pptExiting"))
                    running = False
                    continue

                case "start":
                    if start():
                        print("Inbox has started")
                    else:
                        print("Inbox failed to start")
                case "ping":
                    if ping():
                        print("Inbox is running")
                    else:
                        print("Inbox is NOT running")
                case "stop":
                    stop()
                    print("Inbox has stopped")
                case "ls" | "list":
                    chats = listChats()
                    print(_formatChats(chats))
                case "read":
                    chat = getMsgs(inp[1], int(inp[2]))
                    print(chat)
                case "send":
                    tf = sendMsg(inp[1], inp[2])
                    print("Message send:", tf)
                case "defaults":
                    FileReader.makeSettings()
                case _:
                    print("UNKNOWN: " + inp[0])
            
            # Add a line for spacing
            print(lang.getString("pptEndReq"))
            print()
        except Exception as e:
            print(e)