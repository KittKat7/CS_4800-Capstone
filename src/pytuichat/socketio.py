import os, socket
import debug
from filereader import FileReader
from stupid import STUPID
from idiot import IDIOT

# 0o prefix denotes octal
MSGPERMS: int = 0o666
CLIPERMS: int = 0o600


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
    if debug.isDebug:
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
    if debug.isDebug:
        return

    sl: list[STUPID] = STUPID.encodeStupid(data)
    byteData: list[bytes] = [t.toBytes() for t in sl]

    # Send all packets to server (as bytes)
    for p in byteData:
        print("sending!")
        client.sendall(p)

def recieveSocketIO(socket: socket.socket) -> str:
    """
    Recieve data from a socket.
    """
    recievingData: bool = True

    pl: list[STUPID] = []
    while recievingData:
        print("...ing")
        socket.recv
        pb: bytes = socket.recv(STUPID.PACKET_SIZE)
        p: STUPID = STUPID.fromBytes(pb)
        pl.append(p)
        print(p.getSeg(), p.getTotalSeg())
        if p.getSeg() >= p.getTotalSeg():
            print("TRUE")
            recievingData = False
    
    return STUPID.decodeStupid(pl)

def createMessageClient(contact: str) -> socket.socket:
    print("11")
    path: str = buildMsgSocketPath(contact)
    print("12")
    client: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    print("13")
    client.setblocking(False)
    client.connect(path)
    print("14")
    return client

def createCliClient() -> socket.socket:
    path: str = buildCliSocketPath()
    client: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(path)
    return client

def singleCliCommand(idiot: IDIOT) -> IDIOT:
    client: socket.socket = createCliClient()
    sendSocketIO(client, idiot.toString())

    return IDIOT.fromString(recieveSocketIO(client))