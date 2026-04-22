import os, socket
from pytuichat.filereader import FileReader
from pytuichat.stupid import STUPID
from pytuichat.idiot import IDIOT
from pytuichat.debug import *

# 0o prefix denotes octal
MSGPERMS: int = 0o666
CLIPERMS: int = 0o600
SOCKETIO_TIMEOUT: int = 5

def buildMsgSocketPath(username: str) -> str:
    """
    Builds and returns a string path to the socket for the given username.
    """
    return "/tmp/pytuichat_" + username + ".sock"

def buildCliSocketPath() -> str:
    """
    Builds and returns a string path to the socket used for cli interactions
    by the user.
    """
    return FileReader.getDataDir() + "/pytuichat.sock"

def createSocket(path: str, perms: int) -> socket.socket:
    """
    Creates and returns a socket at the given file path. If the file already
    exists, unlink it, then create the socket.
    """
    if isDebug:
        return socket.socket()

    # Check if socket file exists
    if not os.path.isfile(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    # unlink socket path
    try:
        os.unlink(path)
    except OSError:
        if os.path.exists(path):
            raise

    # create socket
    msgSocket: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    msgSocket.bind(path)
    os.chmod(path, perms)
    return msgSocket

def sendSocketIO(client: socket.socket, data: str):
    """
    Sends a message to a socket, throws an exception if sending fails, otherwise
    returns the recieved message back.
    """
    # TODO add to queue
    if isDebug:
        return

    sl: list[STUPID] = STUPID.encodeStupid(data)
    byteData: list[bytes] = [t.toBytes() for t in sl]

    # Send all packets to server (as bytes)
    for p in byteData:
        client.sendall(p)

def recieveSocketIO(socket: socket.socket) -> str:
    """
    Recieve data from a socket.
    """
    recievingData: bool = True

    plist: list[STUPID] = []
    while recievingData:

        # Recieve the packet length in bytes
        plenb: bytes = socket.recv(STUPID.LEN_BYTES)
        plen: int = int.from_bytes(plenb) - STUPID.LEN_BYTES

        # If a negative length, then stop recieving
        if not plenb:
            recievingData = False
            continue

        # Recieve the rest of the packet
        pbytes: bytes = socket.recv(plen)

        # Make the packet object and add to list
        p: STUPID = STUPID.fromBytes(plenb + pbytes)
        plist.append(p)

        # If its the last segment, stop recieving
        if p.isLastSeg():
            recievingData = False

        if p.getLastSeg() == -1:
            raise Exception("TODO") # TODO

    return STUPID.decodeStupid(plist)

def createMessageClient(contact: str) -> socket.socket:
    """
    Creates a socket client to send messages. If it fails, an error will be
    thrown.
    """
    path: str = buildMsgSocketPath(contact)
    client: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(path)
    return client

def createCliClient() -> socket.socket:
    path: str = buildCliSocketPath()
    client: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(path)
    return client

def singleCliCommand(client: socket.socket | None, idiot: IDIOT) -> IDIOT:
    newSocket: bool = not client
    if newSocket:
        client = createCliClient()
    sendSocketIO(client, idiot.toString())

    strt: str = recieveSocketIO(client)
    print(strt)

    if newSocket:
        client.close()

    return IDIOT.fromString(strt)