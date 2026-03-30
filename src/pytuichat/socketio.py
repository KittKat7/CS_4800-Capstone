import os, socket
import debug
from filereader import FileReader

MSGPERMS: int = 666
CLIPERMS: int = 600


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
    return FileReader.getConfigDir() + "/pytuichat.sock"

def createSocket(path: str, perms: int) -> socket.socket:
    """
    Creates and returns a socket at the given file path. If the file already
    exists, unlink it, then create the socket.
    """
    if debug.isDebug:
        return socket.socket()

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

def sendSocketIO(data: str, socket_path: str) -> str:
    """
    Sends a message to a socket, throws an exception if sending fails, otherwise
    returns the recieved message back.
    """
    # TODO add to queue
    if debug.isDebug:
        return ""

    # Create the Unix socket client
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    response: str = ""

    try:
        # Connect to the server
        # If it fails, return false
        client.connect(socket_path)

        # Send a message to the server
        client.sendall(data.encode())

        # Receive a response from the server
        response = client.recv(1024).decode()
    except:
        client.close()
        raise Exception("Failed to send")
    finally:
        # Close the connection
        client.close()
    return response

def sendSocketIOMsg(data: str, contact: str) -> str:
    return sendSocketIO(data, buildMsgSocketPath(contact))