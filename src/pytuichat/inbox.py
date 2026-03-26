import socket
import os
import json
import asyncio
import threading

from message import *
from contact import *
from chat import *
from spit import *
from filereader import *

# class _InboxOperation(Enum):
#     SEND_MESSAGE = None
#     RECIEVE_MESSAGE = None

class Inbox:

    # Debug mode
    isDebug: bool

    # Initiated
    _isInit: bool = False

    # Fields
    _contacts: dict[str, Contact]
    _chats: dict[str, Chat|None]
    _outbox: list[DeliveryMessage]

    # _operationQueue: list[_InboxOperation] = []

    _msgThread: threading.Thread
    _cliThread: threading.Thread

    _msgSocket: socket.socket
    _cliSocket: socket.socket

    @staticmethod
    def runInbox(isDebug: bool = False) -> None:
        """
        Runs the setup for an inbox program
        """
        # Make sure init is only run once
        if Inbox._isInit:
            return
        Inbox._isInit = True

        # If launching in debug, set the flag
        Inbox.isDebug = isDebug

        Inbox._contacts = FileReader.getContacts()
        tmpChatNames: list[str] = FileReader.getChatTitles()
        for n in tmpChatNames:
            Inbox._chats[n] = None
        Inbox._outbox = FileReader.getUnsent()

        # Set up and run the messaging socket and threat
        Inbox._msgSocket = Inbox._createMsgSocket()
        Inbox._msgSocket.listen(1)
        Inbox._msgThread = threading.Thread(
            target = asyncio.gather,
            args=(Inbox._sendMessageLoop, Inbox._messageRecieveLoop)
        )

        # TODO
        # Set up and run the cli socket and threat
        Inbox._cliSocket = Inbox._createCliSocket()
        # Inbox._cliSocket.listen(1)
        # Inbox._cliThread = threading.Thread(
        #     target=#TODO
        # )

    @staticmethod
    def buildMsgSocketPath(username: str) -> str:
        """
        Builds and returns a string path to the socket for the given username.
        """
        return "/tmp/pytuichat_" + username + ".sock"

    @staticmethod
    def buildCliSocketPath() -> str:
        """
        Builds and returns a string path to the socket used for cli interactions
        by the user.
        """
        return FileReader.getConfigDir() + "/pytuichat.sock"

    @staticmethod
    def _createMsgSocket() -> socket.socket:
        socketPath: str = Inbox.buildMsgSocketPath(os.getlogin())

        # unlink socket path
        try:
            os.unlink(socketPath)
        except OSError:
            if os.path.exists(socketPath):
                raise

        # create socket
        msgSocket: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        msgSocket.bind(socketPath)
        os.chmod(socketPath, 666)
        return msgSocket

    @staticmethod
    def _createCliSocket() -> socket.socket:
        socketPath: str = Inbox.buildCliSocketPath()

        # unlink socket path
        try:
            os.unlink(socketPath)
        except OSError:
            if os.path.exists(socketPath):
                raise

        # create socket
        msgSocket: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        msgSocket.bind(socketPath)
        return msgSocket

    @staticmethod
    def _findOrCreateContact(username: str) -> Contact:
        """
        When given a contact name, either find an already known contact, or
        create a new one. Then return the contact.
        """
        if username in Inbox._contacts:
            return Inbox._contacts[username]

        # No known contact was found, create one and add it to the contact list
        c: Contact = Contact(username)
        Inbox._contacts[username] = c
        # Save contact persistantly
        FileReader.updateContacts(Inbox._contacts)
        # Return the new contact
        return c

    @staticmethod
    def _findOrCreateChat(chatID: str) -> Chat:
        """
        Find a specific chat. If the chat does not exist, create and return it.
        """
        # Try to find existing chat, if found, return it
        if chatID in Inbox._chats:
            if Inbox._chats[chatID] is None:
                Inbox._chats[chatID] = FileReader.getChat(chatID)
            return cast(Chat, Inbox._chats[chatID])


        # TODO optimize
        # No chat was found, create a new one and add it to the list
        cl: list[str] = Chat.decodeParticipantID(chatID)
        for c in cl:
            Inbox._findOrCreateContact(c)
        chh: Chat = Chat(cl)
        # Save chat persistantly
        FileReader.updateChat(chh)
        # Return new chat
        return chh
    
    @staticmethod
    def ping(contact: Contact) -> bool:
        """
        Returns true if able to ping the socket for the contact.
        """
        # Connect to the contacts server if possible
        socket_path = Inbox.buildMsgSocketPath(contact.getUsername())
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

    @staticmethod
    async def _sendMessageLoop() -> None:
        """
        This loop runs on a timer and will periodically try to resend unsent
        messages.
        """
        outboxLength: int = len(Inbox._outbox)
        updatePersist: bool = False
        while True:
            if len(Inbox._outbox) != outboxLength:
                updatePersist = True

            for dm in Inbox._outbox:
                if Inbox._sendMessage(dm):
                    updatePersist = True

            if updatePersist:
                FileReader.updateUnsentList(Inbox._outbox)
                updatePersist = False

            await asyncio.sleep(60)

    @staticmethod
    def _sendMessage(message: DeliveryMessage) -> bool:
        """
        Sends a message by adding it to the outbox. The message send loop will
        send the message to contacts when possible.
        """

        sendTo: list[str] = message.getSendingTo()
        for c in sendTo:
            sent: bool = Inbox._deliverMessage(
                Inbox._findOrCreateContact(c),
                message,
            )
            if sent:
                message.sentTo(c)
        
        if not message.getSendingTo():
            Inbox._outbox.remove(message)
            return True

        if message not in Inbox._outbox:
            Inbox._outbox.append(message)

        return False

    @staticmethod
    def _deliverMessage(contact: Contact, message: DeliveryMessage) -> bool:
        """
        Deliver a message to the contact. If the message delivery fails, return
        false. Otherwise return true.
        """
        # Set the path for the Unix socket
        socket_path = Inbox.buildMsgSocketPath(contact.getUsername())

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

    @staticmethod
    def _handleConnect() -> None:
        """
        Waits for a connection. When a connection is made, handles reading and
        using the connection.
        """

        # Wait for in inbound connection
        connection = Inbox._msgSocket.accept()[1]

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
                        Inbox._onMessageRecieved(dmessage)
                        response = SPIT.Status.OK
                    case _:
                        raise Exception("OH NO")

                # Send a response back to the client
                spitResponse: SPIT = SPIT(SPIT.Type.STATUS, response)
                connection.sendall(spitResponse.toString().encode())
        finally:
            # close the connection
            connection.close()

    @staticmethod
    def _messageRecieveLoop() -> None:
        while True:
            Inbox._handleConnect()
    
    @staticmethod
    def _onMessageRecieved(dmessage: DeliveryMessage) -> None:
        """
        Handles when a message is recieved. Provided a Delivery Message, add the
        message to the relevent chat.
        """
        # TODO
        print("Recieved message: " + str(dmessage.getMessage().getContent()))
        c: Chat = Inbox._findOrCreateChat(dmessage.getChatID())
        c.updateMessageHistory(dmessage.getMessage())






