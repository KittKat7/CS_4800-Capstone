import socket
import getpass
import asyncio
import traceback

from pytuichat.message import *
from pytuichat.contact import *
from pytuichat.chat import *
from pytuichat.spit import *
from pytuichat.idiot import *
from pytuichat.filereader import *
from pytuichat.settings import *
from pytuichat.debug import *
from pytuichat.socketio import *

class Inbox:

    # Initiated
    _isInit: bool = False
    _isRunning: bool

    # Fields
    _contacts: dict[str, Contact]
    _chats: dict[str, Chat]
    _outbox: list[DeliveryMessage]
    _newOutbox: list[DeliveryMessage]
    _settingsManager: SettingsManager
    _connections: list[socket.socket]
    _updates: list[str] # a list of ids for chats that have updates

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
        isDebug = isDebug

        Inbox._isRunning = True

        Inbox._contacts = FileReader.getContacts()
        Inbox._chats = {}
        tmpChatNames: list[str] = FileReader.getChatTitles()
        for n in tmpChatNames:
            Inbox._chats[n] = FileReader.getChat(n)
        Inbox._outbox = FileReader.getUnsent()
        Inbox._newOutbox = []

        # Set up and run the messaging socket
        Inbox._msgSocket = Inbox._createMsgSocket()
        Inbox._msgSocket.listen(1)
        Inbox._msgSocket.setblocking(False)

        # Set up and run the cli socket
        Inbox._cliSocket = Inbox._createCliSocket()
        Inbox._cliSocket.listen(1)
        Inbox._cliSocket.setblocking(False)

        print("Inbox started")
        Inbox._connections = []
        Inbox._updates = []
        Inbox._startHeartbeat()

    @staticmethod
    def getSettingsManager() -> SettingsManager:
        return Inbox._settingsManager

    @staticmethod
    def ping(contact: Contact) -> bool:
        """
        Returns true if able to ping the socket for the contact.
        """
        # Connect to the contacts server if possible
        # TODO handle debugs
        if isDebug:
            return True

        try:
            client: socket.socket = createMessageClient(contact.getUsername())
        except:
            return False

        spit: SPIT = SPIT(SPIT.Type.PING, "")

        # Send a message to the server
        sendSocketIO(client, spit.toString())

        # Receive a response from the server
        response: str = recieveSocketIO(client)
        print(f'Ping response: {response}')
        client.close()
        return True

    @staticmethod
    def _createMsgSocket() -> socket.socket:
        """
        Creates and returns the Msg socket.
        """
        socketPath: str = buildMsgSocketPath(getpass.getuser())
        s: socket.socket = createSocket(socketPath, MSGPERMS)
        return s

    @staticmethod
    def _createCliSocket() -> socket.socket:
        """
        Creates and returns the CLI socket.
        """
        socketPath: str = buildCliSocketPath()
        s: socket.socket = createSocket(socketPath, CLIPERMS)
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

        # No chat was found, create a new one and add it to the list
        cl: list[str] = Chat.decodeParticipantID(chatID)
        for c in cl:
            Inbox._findOrCreateContact(c)
        chh: Chat = Chat(cl)
        # Save chat persistantly
        Inbox._chats[chh.getUniqueID()] = chh
        FileReader.updateChat(chh)
        # Inbox._updates.append(chh.getUniqueID())
        # Return new chat
        return chh

    @staticmethod
    def _sendAllMessages() -> None:
        """
        Tries to send all messages in the outbox.
        """
        outboxLength: int = len(Inbox._outbox)
        updatePersist: bool = False

        Inbox._outbox = Inbox._newOutbox + Inbox._outbox;
        Inbox._newOutbox = []

        for dm in Inbox._outbox:
            if Inbox._sendMessage(dm):
                updatePersist = True

        if len(Inbox._outbox) != outboxLength:
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

        messageChanged: bool = False
        # if sending to self...
        if getpass.getuser() in message.getSendingTo():
            message.sentTo(getpass.getuser())
            messageChanged = True

        sendTo: list[str] = message.getSendingTo()
        for c in sendTo:
            spit: SPIT = SPIT(SPIT.Type.MESSAGE, message.toJsonObj())

            client: socket.socket
            try:
                client = createMessageClient(c)
            except:
                continue

            sendSocketIO(client, spit.toString())
            responseStr: str = recieveSocketIO(client)
            client.close()

            try:
                # Receive a response from the server
                response: SPIT = SPIT.fromString(responseStr)
                if response.data != SPIT.Status.OK:
                    continue
            except:
                continue

            # Fail cases will continue to next iteration of the loop, leaving
            # this to run when it succeeds
            message.sentTo(c)
            messageChanged = True
        
        ch: Chat = Inbox._findOrCreateChat(message.getChatID())
        mid: int = ch.getMessageIdByDate(message.getMessage().getSent())
        m: Message = ch.getMessageHistory()[mid]
        # If the sent timestamp with the timeout is passed by the current date,
        # then timeout the message.
        timeout: bool = (message.getMessage().getSent() + Message.TIMEOUT).timestamp() < datetime.now().timestamp() and len(message.getSendingTo()) > 0
        if not message.getSendingTo():
            if message in Inbox._outbox:
                Inbox._outbox.remove(message)
            m.updateStatus(MessageStatus.SENT)
            messageChanged = True
        
        if timeout:
            m.updateStatus(MessageStatus.TIMEOUT)
            messageChanged = True
        
        if messageChanged:
            print("write!")
            ch.setMessageById(mid, m)
            FileReader.updateChat(ch)

            Inbox._updates.append(ch.getUniqueID())
        
        if not message.getSendingTo():
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
            dataStr: str = recieveSocketIO(connection)

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
                    # TODO
                    raise Exception("OH NO")

            # Send a response back to the client
            spitResponse: SPIT = SPIT(SPIT.Type.STATUS, response)
            sendSocketIO(connection, spitResponse.toString())
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
        msg: Message = dmessage.getMessage()
        msg.updateStatus(MessageStatus.UNREAD)
        c.updateMessageHistory(msg)
        Inbox._updates.append(c.getUniqueID())
        FileReader.updateChat(c)

    @staticmethod
    def _cliCheck() -> None:
        try:
            connection = Inbox._cliSocket.accept()[0]
            connection.setblocking(False)
            Inbox._connections.append(connection)
        except:
            ""

        rml: list[socket.socket] = []
        for c in Inbox._connections:
            try:
                if hasData(c):
                    Inbox._handleCliRecieved(c)
            except:
                rml.append(c)
        for c in rml:
            Inbox._connections.remove(c)


    @staticmethod
    def _handleCliRecieved(connection: socket.socket) -> None:
        """
        Waits and handles connections from the CLI.
        """

        # Wait for in inbound connection
        print('Connection from', str(connection))

        try:
            dataStr: str = recieveSocketIO(connection)

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
                    sendSocketIO(connection, idiotResponse.toString())

                case IDIOT_TYPE.SEND_MSG:
                    dm: DeliveryMessage = DeliveryMessage.fromJsonObj(json.loads(idiot.data))
                    c: Chat = Inbox._findOrCreateChat(dm.getChatID())
                    m: Message = dm.getMessage()
                    m.updateStatus(MessageStatus.SENDING)
                    c.updateMessageHistory(dm.getMessage())

                    Inbox._newOutbox.append(dm)
                    r = "sending"
                    idiotResponse: IDIOT = IDIOT(
                        IDIOT_TYPE.SEND_MSG,
                        r)
                    sendSocketIO(connection, idiotResponse.toString())

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
                    sendSocketIO(connection, idiotResponse.toString())

                case IDIOT_TYPE.PING:
                    idiotResponse: IDIOT = IDIOT(
                        IDIOT_TYPE.PING, "")
                    sendSocketIO(connection, idiotResponse.toString())
                
                case IDIOT_TYPE.CREATE_CHAT:
                    chatid: str = idiot.data
                    chat: Chat = Inbox._findOrCreateChat(chatid)
                    FileReader.updateChat(chat)
                    idiotResponse: IDIOT = IDIOT(
                        IDIOT_TYPE.CREATE_CHAT, chat.getUniqueID())
                    sendSocketIO(connection, idiotResponse.toString())

                case _:
                    raise Exception("OH NO")
        except Exception as e:
            Inbox._connections.remove(connection)
            print(e)
            print(traceback.format_exc())
    
    @staticmethod
    def _sendClientUpdates() -> None:
        """
        Sends the updates for chats to all connected clients.
        """
        for u in Inbox._updates:
            for client in Inbox._connections:
                sendSocketIO(client, IDIOT(IDIOT_TYPE.UPDATE, u).toString())
        Inbox._updates = []

    @staticmethod
    def _startHeartbeat() -> None:
        """
        Starts the hearbeat of the inbox.
        """
        asyncio.run(Inbox._heartbeat())
        # asyncio.run(Inbox._msgHeartbeat())

    @staticmethod
    async def _heartbeat() -> None:
        """
        Runs every second as a heartbeat.
        """
        MAX_TIME: int = 65535
        MAX_LOWER: int = -65536
        CHECK_CLI_TIME: int = 1

        RESEND_TIME: int = 5
        CHECK_INBOX_TIME: int = 1
        time: float = 0
        
        try:
            while Inbox._isRunning:
                await asyncio.sleep(0.001)

                if time % CHECK_CLI_TIME == 0:
                    Inbox._cliCheck()

                if time % CHECK_CLI_TIME == 0:
                    Inbox._sendClientUpdates()

                # Handle resent heartbeat
                if time % RESEND_TIME == 0 or Inbox._newOutbox:
                    Inbox._sendAllMessages()

                # Handle check inbox timeout
                if time % CHECK_INBOX_TIME == 0:
                    Inbox._handleMsgConnect()

                # If time passes MAX_TIME reset the time to 0
                if time >= MAX_TIME:
                    time = MAX_LOWER
                # Increment the time
                time = round(time + 0.1, 1)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            Inbox._isRunning = False