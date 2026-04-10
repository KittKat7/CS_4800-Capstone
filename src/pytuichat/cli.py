
import sys
import os
import subprocess
import getpass

from inbox import *
from filereader import *
import lang
from socketio import singleCliCommand

args = sys.argv[1:]

lang.setLangMap("en_us")

def ping() -> bool:
    """
    Returns true if able to ping the socket for the inbox
    """
    # Connect to the contacts server if possible
    socket_path = socketio.buildCliSocketPath()
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect(socket_path)

        client.close()
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
        return True

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
    strTime: str = str(msg.getSent().strftime("%Y%m%d %I%M%p"))

    return f"{mStatus} {strTime} {msg.getSender()}: {msg.getContent()}"

def getMsgs(id: str, n: int = 100) -> str:
    """
    TODO
    """
    response: IDIOT = singleCliCommand(IDIOT(IDIOT_TYPE.READ_MSGS, json.dumps({"id": id, "n": n})))
    
    msgStr: str = ""
    for m in json.loads(response.data):
        msgStr += _formatMessage(Message.fromJsonObj(m)) + "\n"
    return msgStr

def sendMsg(chatid: str, msg: str) -> str:
    """
    TODO
    """
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

if __name__ == "__main__":
    match args[0]:
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
        case "list":
            chats = listChats()
            print(chats)
        case "read":
            chat = getMsgs(args[1], int(args[2]))
            print(chat)
        case "send":
            tf = sendMsg(args[1], args[2])
            print("Message send:", tf)
        case _:
            print("UNKNOWN: " + args[0])
