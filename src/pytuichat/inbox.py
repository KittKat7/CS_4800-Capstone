import socket
import os
import json

from message import *
from contact import *
from chat import *
from spit import *


class Inbox:
    def __init__(self):
        self._contacts: list[str]
        self._chats: list[Chat]

    def getChats(self) -> list[Chat]:
        return self._chats

    def _findOrCreateChat(self, contacts: list[Contact]) -> Chat:
        """
        Find a specific chat. If the chat does not exist, create and return it.
        """
        for ch in self._chats:
            if len(ch._participants) == len(contacts):
                isMatch: bool = True
                for c in contacts:
                    if c not in ch._participants:
                        isMatch = False
                if isMatch:
                    return ch

        # TODO add specific make chat method
        chh: Chat = Chat(contacts)
        return chh
    
    def sendMessage(self, contact: Contact, message: DeliveryMessage) -> None:
        """
        """
        # TODO
        print("Message send: " + str(self._deliverMessage(contact, message)))
    
    def isContactSendable(self, contact: Contact) -> bool:
        """
        """
        # TODO
        return False

    def _deliverMessage(self, contact: Contact, message: DeliveryMessage) -> bool:
        """
        Deliver a message to the contact. If the message delivery fails, return
        false. Otherwise return true.
        """
        # TODO

        # Set the path for the Unix socket
        socket_path = "/tmp/pytuichat_" + contact.getUsername()

        # Create the Unix socket client
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Connect to the server
        # If it fails, return false
        try:
            client.connect(socket_path)
        except:
            return False

        spit: SPIT = SPIT(SPIT.Type.MESSAGE, json.dumps(message.toJsonObj()))

        # Send a message to the server
        client.sendall(spit.toString().encode())

        # Receive a response from the server
        response = client.recv(1024)
        print(f'Received response: {response.decode()}')
        # TODO handle recieved spit
        # Close the connection
        client.close()
        return True

    def _handleConnect(self, server: socket.socket) -> None:
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
                spit: SPIT = SPIT.fromString(dataStr)

                # Handle type of SPIT
                
                response: object

                match spit.type:
                    case SPIT.Type.PING:
                        response = True
                    case SPIT.Type.MESSAGE:
                        dmessage: DeliveryMessage = DeliveryMessage.fromJsonObj(json.loads(spit.data))
                        self._onMessageRecieved(dmessage)
                        response = True
                    case _:
                        raise Exception("OH NO")

                # Send a response back to the client
                spitResponse: SPIT = SPIT(SPIT.Type.STATUS, response)
                connection.sendall(spitResponse.toString().encode())
        finally:
            # close the connection
            connection.close()
    
    def _onMessageRecieved(self, dmessage: DeliveryMessage) -> None:
        """
        Handles when a message is recieved. Provided a Delivery Message, add the
        message to the relevent chat.
        """
        # TODO
        print("Recieved message: " + str(dmessage._message._content))
        c: Chat = self._findOrCreateChat(dmessage._recipients)
        c.updateMessageHistory(dmessage.getMessage)

    @staticmethod
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
            inbox._handleConnect(server)






