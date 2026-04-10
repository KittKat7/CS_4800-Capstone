import socket
import getpass
import asyncio
import threading

from message import *
from contact import *
from chat import *
from spit import *
from idiot import *
from filereader import *
import debug
import socketio

# class _InboxOperation(Enum):
#     SEND_MESSAGE = None
#     RECIEVE_MESSAGE = None

class Inbox:

    # Initiated
    _isInit: bool = False
    _isRunning: bool

    # Fields
    _contacts: dict[str, Contact]
    _chats: dict[str, Chat]
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
        debug.isDebug = isDebug

        Inbox._isRunning = True

        Inbox._contacts = FileReader.getContacts()
        Inbox._chats = {}
        tmpChatNames: list[str] = FileReader.getChatTitles()
        for n in tmpChatNames:
            Inbox._chats[n] = FileReader.getChat(n)
        Inbox._outbox = FileReader.getUnsent()

        # Set up and run the messaging socket and threat
        Inbox._msgSocket = Inbox._createMsgSocket()
        Inbox._msgSocket.listen(1)
        Inbox._msgSocket.setblocking(False)
        Inbox._msgThread = threading.Thread(
            target = Inbox._startHeartbeat
        )

        # TODO
        # Set up and run the cli socket and threat
        Inbox._cliSocket = Inbox._createCliSocket()
        Inbox._cliSocket.listen(1)
        Inbox._cliThread = threading.Thread(
            target = Inbox._cliRecieved
        )

        Inbox._msgThread.start()
        Inbox._cliThread.start()
        print("Inbox started")


    @staticmethod
    def ping(contact: Contact) -> bool:
        """
        Returns true if able to ping the socket for the contact.
        """
        # Connect to the contacts server if possible
        # TODO handle debugs
        if debug.isDebug:
            return True

        try:
            client: socket.socket = socketio.createMessageClient(contact.getUsername())
        except:
            return False

        spit: SPIT = SPIT(SPIT.Type.PING, "")

        # Send a message to the server
        socketio.sendSocketIO(client, spit.toString())

        # Receive a response from the server
        response: str = socketio.recieveSocketIO(client)
        print(f'Ping response: {response}')
        client.close()
        return True

    @staticmethod
    def _createMsgSocket() -> socket.socket:
        """
        Creates and returns the Msg socket.
        """
        socketPath: str = socketio.buildMsgSocketPath(getpass.getuser())
        s: socket.socket = socketio.createSocket(socketPath, socketio.MSGPERMS)
        return s

    @staticmethod
    def _createCliSocket() -> socket.socket:
        """
        Creates and returns the CLI socket.
        """
        socketPath: str = socketio.buildCliSocketPath()
        s: socket.socket = socketio.createSocket(socketPath, socketio.CLIPERMS)
        return s

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
            return Inbox._chats[chatID]

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
    def _sendAllMessages() -> None:
        """
        Tries to send all messages in the outbox.
        """
        outboxLength: int = len(Inbox._outbox)
        updatePersist: bool = False
        if len(Inbox._outbox) != outboxLength:
            updatePersist = True

        for dm in Inbox._outbox:
            if Inbox._sendMessage(dm):
                updatePersist = True

        if updatePersist:
            FileReader.updateUnsentList(Inbox._outbox)
            updatePersist = False

    @staticmethod
    def _sendMessage(message: DeliveryMessage) -> bool:
        """
        Sends a message by adding it to the outbox. The message send loop will
        send the message to contacts when possible.
        """
        sendTo: list[str] = message.getSendingTo()
        for c in sendTo:
            spit: SPIT = SPIT(SPIT.Type.MESSAGE, message.toJsonObj())

            try:
                client: socket.socket = socketio.createMessageClient(c)
                socketio.sendSocketIO(client, spit.toString())
            except:
                return False

            responseStr: str = socketio.recieveSocketIO(client)

            client.close()

            try:
                # Receive a response from the server
                response: SPIT = SPIT.fromString(responseStr)
                if response.data == SPIT.Status.OK:
                    print("Message sent successfully")
                    message.getMessage().updateStatus(MessageStatus.SENT)
                else:
                    print("Message not recieved")
                    continue
            except:
                continue

            # Fail cases will continue, leaving this to run when it succeeds
            message.sentTo(c)
        
        if not message.getSendingTo():
            if message in Inbox._outbox:
                Inbox._outbox.remove(message)
            ch: Chat = Inbox._findOrCreateChat(message.getChatID())
            for m in ch.getMessageHistory():
                if m.getSent() == message.getMessage().getSent():
                    m.updateStatus(MessageStatus.SENT)
                    break
            return True

        if message not in Inbox._outbox:
            Inbox._outbox.append(message)

        return False

    @staticmethod
    def _handleMsgConnect() -> None:
        """
        Handle a connection if there is one. When a connection is made, handles
        reading and using the connection.
        """

        try:
            # Wait for in inbound connection
            connection = Inbox._msgSocket.accept()[0]
            print('Connection from', str(connection))
        except:
            return

        try:
            # receive data from the client
            dataStr: str = socketio.recieveSocketIO(connection)

            spit: SPIT = SPIT.fromString(dataStr)

            match spit.type:
                case SPIT.Type.PING:
                    response = SPIT.Status.OK
                case SPIT.Type.MESSAGE:
                    dmessage: DeliveryMessage = DeliveryMessage.fromJsonObj(
                        spit.data)
                    Inbox._recievedMessage(dmessage)
                    response = SPIT.Status.OK
                case _:
                    raise Exception("OH NO")

            # Send a response back to the client
            spitResponse: SPIT = SPIT(SPIT.Type.STATUS, response)
            socketio.sendSocketIO(connection, spitResponse.toString())
        finally:
            # close the connection
            connection.close()
    
    @staticmethod
    def _recievedMessage(dmessage: DeliveryMessage) -> None:
        """
        Handles when a message is recieved. Provided a Delivery Message, add the
        message to the relevent chat.
        """
        # TODO
        print("Recieved message: " + str(dmessage.getMessage().getContent()))
        c: Chat = Inbox._findOrCreateChat(dmessage.getChatID())
        c.updateMessageHistory(dmessage.getMessage())
        FileReader.updateChat(c)

    @staticmethod
    def _cliRecieved() -> None:
        """
        Basically a while true loop to handle all cli commands.
        """
        try:
            while Inbox._isRunning:
                Inbox._handleCliRecieved()
        except:
            Inbox._isRunning = False

    @staticmethod
    def _handleCliRecieved() -> None:
        """
        Waits and handles connections from the CLI.
        """

        # Wait for in inbound connection
        connection = Inbox._cliSocket.accept()[0]
        print('Connection from', str(connection))

        try:

            # receive data from the client
            dataStr: str = socketio.recieveSocketIO(connection)
            print(dataStr)

            idiot: IDIOT = IDIOT.fromString(dataStr)

            # Handle the incoming idiot
            match idiot.type:
                # When the STOP command is recieved
                case IDIOT_TYPE.STOP:
                    Inbox._isRunning = False
                    raise Exception("Shutting Down!!!")

                case IDIOT_TYPE.LIST_CHATS:
                    idiotResponse: IDIOT = IDIOT(
                        IDIOT_TYPE.LIST_CHATS,
                        json.dumps([Inbox._chats[t].getHeaderJsonObj() for t in Inbox._chats]))
                    socketio.sendSocketIO(connection, idiotResponse.toString())

                case IDIOT_TYPE.SEND_MSG:
                    dm: DeliveryMessage = DeliveryMessage.fromJsonObj(json.loads(idiot.data))
                    c: Chat = Inbox._findOrCreateChat(dm.getChatID())
                    m: Message = dm.getMessage()
                    m.updateStatus(MessageStatus.SENDING)
                    c.updateMessageHistory(dm.getMessage())
                    FileReader.updateChat(c)
                    r: bool = Inbox._sendMessage(dm)
                    idiotResponse: IDIOT = IDIOT(
                        IDIOT_TYPE.SEND_MSG,
                        str(r))
                    socketio.sendSocketIO(connection, idiotResponse.toString())

                case IDIOT_TYPE.READ_MSGS:
                    # Get data from recieved message
                    idata: dict[str, object] = json.loads(idiot.data)
                    id: str = cast(str, idata["id"])
                    n: int = cast(int, idata["n"])

                    history: list[Message]
                    if not Inbox._chats[id]:
                        history = []
                    else:
                        history = Inbox._chats[id].readMessages(n)
                    
                    responseJson: list[object] = []
                    for m in history:
                        responseJson.append(m.toJsonObj())
                    # responseStr: str = ""
                    # for m in history:
                    #     responseStr += f"{str(m.getSent().strftime("%Y%m%d %I%M%p"))} {m.getSender()}: {m.getContent()}\n"

                    idiotResponse: IDIOT = IDIOT(
                        IDIOT_TYPE.LIST_CHATS, json.dumps(responseJson))
                    socketio.sendSocketIO(connection, idiotResponse.toString())

                case _:
                    raise Exception("OH NO")

        finally:
            # close the connection
            connection.close()

    @staticmethod
    def _startHeartbeat() -> None:
        """
        Starts the hearbeat of the inbox.
        """
        asyncio.run(Inbox._heartbeat())

    @staticmethod
    async def _heartbeat() -> None:
        """
        Runs every second as a heartbeat.
        """
        MAX_TIME: int = 65535
        MAX_LOWER: int = -65536
        RESEND_TIME: int = 60
        CHECK_INBOX_TIME: int = 1

        time: int = 0
        
        try:
            while Inbox._isRunning:
                await asyncio.sleep(1)

                # Handle resent heartbeat
                if time % RESEND_TIME == 0:
                    # TODO resend things
                    Inbox._sendAllMessages()

                # Handle check inbox timeout
                if time % CHECK_INBOX_TIME == 0:
                    # TODO check inbox
                    Inbox._handleMsgConnect()

                # If time passes MAX_TIME reset the time to 0
                if time >= MAX_TIME:
                    time = MAX_LOWER
                # Increment the time
                time += 1
        except:
            Inbox._isRunning = False




