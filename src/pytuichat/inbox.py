import socket
import os
import json

from message import *
from contact import *
from chat import *
from spit import *


class Inbox:
    def __init__(self):
        self._contacts: list[Contact] = []
        self._chats: list[Chat] = []
        self._outbox: list[DeliveryMessage] = FileReader.getUnsent()

    def getChats(self) -> list[Chat]:
        return self._chats

    def _findOrCreateContact(self, username: str) -> Contact:
        """
        When given a contact name, either find an already known contact, or
        create a new one. Then return the contact.
        """
        # Try to find an already known contact, if found, return it
        for c in self._contacts:
            if c.getUsername() == username:
                return c
        
        # No known contact was found, create one and add it to the contact list
        c: Contact = Contact(username)
        self._contacts.append(c)
        # Save contact persistantly
        # TODO FILEIO call, save to persistant
        # Return the new contact
        return c

    def _findOrCreateChat(self, chatID: str) -> Chat:
        """
        Find a specific chat. If the chat does not exist, create and return it.
        """
        # Try to find existing chat, if found, return it
        for ch in self._chats:
            if ch.getUniqueID() == chatID:
                return ch

        # No chat was found, create a new one and add it to the list
        chh: Chat = Chat([c.getUsername() for c in self._contacts])
        self._chats.append(chh)
        # Save chat persistantly
        FileReader.updateChat(chh)
        # Return new chat
        return chh
    
    def ping(self, contact: Contact) -> bool:
        """
        Returns true if able to ping the socket for the contact.
        """
        # Connect to the contacts server if possible
        socket_path = "/tmp/pytuichat_" + contact.getUsername()
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(socket_path)
        except:
            return False

        spit: SPIT = SPIT(SPIT.Type.PING, "")

        # Send a message to the server
        client.sendall(spit.toString().encode())

        # Receive a response from the server
        response = client.recv(1024)
        print(f'Ping response: {response.decode()}')
        client.close()
        return True

    def sendMessage(self, contact: Contact, message: DeliveryMessage) -> None:
        """
        Sends a message by adding it to the outbox. The message send loop will
        send the message to contacts when possible.
        """
        self._outbox.append(message)
        FileReader.writeOutbox(self._outbox)

    def _deliverMessage(self, contact: Contact, message: DeliveryMessage) -> bool:
        """
        Deliver a message to the contact. If the message delivery fails, return
        false. Otherwise return true.
        """
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
        response = SPIT.fromString(client.recv(1024).decode())
        
        # Handle recieved SPIT
        recieved: bool = True

        try:
            if response.data == SPIT.Status.OK:
                print("Message sent successfully")
                message.getMessage().updateStatus(MessageStatus.SENT)
            else:
                print("Message not recieved")
                recieved = False
        except:
            recieved = False
        finally:
            # Close the connection
            client.close()
            return recieved

    def _handleConnect(self, server: socket.socket) -> None:
        """TODO"""
        # TODO
        connection = server.accept()[1]

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
                        response = SPIT.Status.OK
                    case SPIT.Type.MESSAGE:
                        dmessage: DeliveryMessage = DeliveryMessage.fromJsonObj(spit.data)
                        self._onMessageRecieved(dmessage)
                        response = SPIT.Status.OK
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
        print("Recieved message: " + str(dmessage.getMessage().getContent()))
        c: Chat = self._findOrCreateChat(dmessage.getChatID())
        c.updateMessageHistory(dmessage.getMessage())

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






