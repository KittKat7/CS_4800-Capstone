import os, socket
import debug

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