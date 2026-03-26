
import sys
import os
import subprocess

from inbox import *
from filereader import *

args = sys.argv[1:]

def ping() -> bool:
    """
    Returns true if able to ping the socket for the inbox
    """
    # Connect to the contacts server if possible
    socket_path = Inbox.buildCliSocketPath()
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

def stop():
    """
    Returns true if able to ping the socket for the inbox
    """
    # Connect to the contacts server if possible
    socket_path = Inbox.buildCliSocketPath()
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect(socket_path)
        client.sendall(IDIOT(IDIOT_TYPE.STOP, "").toString().encode())
        client.close()
        return True
    except Exception:
        return False

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
    case _:
        print("UNKNOWN: " + args[0])
