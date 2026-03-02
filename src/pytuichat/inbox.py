import socket
import os
import json

from message import *
from contact import *
from chat import *


class Inbox:
    def __init__(self):
        self._contacts: list[str]
        self._chats: list[Chat]


    
    def getChats(self) -> list[Chat]:
        return self._chats
    
    def sendMessage(self, contact: Contact, message: Message) -> None:
        """
        """
        # TODO
    
    def isContactSendable(self, contact: Contact) -> bool:
        """
        """
        # TODO
        return False

    def _deliverMessage(self, contact: Contact, message: Message) -> bool:
        """
        """
        # TODO
        return False
    
    def _onMessageRecieved(self, message: Message) -> None:
        """
        """
        # TODO


def runInbox() -> None:

    inbox: Inbox = Inbox()

    # INBOX RUNNER
    # init sockets
    socketPath = "/tmp/pytuichat_" + os.getlogin()

    # unlink socket path
    try:
        os.unlink(socketPath)
    except OSError:
        if os.path.exists(socketPath):
            raise

    # create socker server
    server: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socketPath)
    os.chmod(socketPath, 666)


    server.listen(1)

    while True:
        handleConnect(server, inbox)

def handleConnect(server: socket.socket, inbox: Inbox) -> None:
    """TODO"""
    # TODO
    connection, address = server.accept()

    try:
        print('Connection from', str(connection))

        # receive data from the client
        while True:
            data = connection.recv(1024)
            if not data:
                break
            
            dataStr: str = data.decode()
            dataObj: object = json.loads(dataStr)
            dmessage: DeliveryMessage = DeliveryMessage.fromJsonObj(dataObj)


            # Send a response back to the client
            response = 'Hello from the server!' + address + ";"
            connection.sendall(response.encode())
    finally:
        # close the connection
        connection.close()



runInbox()




