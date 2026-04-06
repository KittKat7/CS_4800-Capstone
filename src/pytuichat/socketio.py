import os, socket
import debug
from filereader import FileReader
from stupid import STUPID

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

def sendSocketIO(data: str, socket_path: str) -> None:
    """
    Sends a message to a socket, throws an exception if sending fails, otherwise
    returns the recieved message back.
    """
    # TODO add to queue
    if debug.isDebug:
        return

    sl: list[STUPID] = STUPID.encodeStupid(data)
    byteData: list[bytes] = [t.toBytes() for t in sl]

    # Create the Unix socket client
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # Connect to the server
    # If it fails, return false
    client.connect(socket_path)

    # Send all packets to server (as bytes)
    for p in byteData:
        client.sendall(p)

def recieveSocketIO(socket: socket.socket) -> str:
    """
    Recieve data from a socket.
    """
    recievingData: bool = True

    pl: list[STUPID] = []
    while recievingData:
        pb: bytes = socket.recv(STUPID.PACKET_SIZE)
        p: STUPID = STUPID.fromBytes(pb)
        pl.append(p)
        if p.getSeg() >= p.getTotalSeg():
            recievingData = False
    
    return STUPID.decodeStupid(pl)

def sendSocketIOMsg(data: str, contact: str) -> None:
    return sendSocketIO(data, buildMsgSocketPath(contact))

def sendSocketIOCli(data: str) -> None:
    return sendSocketIO(data, buildCliSocketPath())