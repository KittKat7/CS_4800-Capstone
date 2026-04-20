from typing import cast
import getpass

from pytuichat.message import *
from pytuichat.contact import *

class Chat:
    def __init__(self, contacts: list[str]):
        if getpass.getuser() not in contacts:
            contacts.append(getpass.getuser())
        contacts.sort()
        self._numUnread: int = 0
        self._participants: list[str] = contacts
        self._history: list[Message] = []

    @staticmethod
    def encodeParticipantID(contactNames: list[str]) -> str:
        """
        Build a unique ID for a chat, from a list of contact names.
        """
        # Remove duplicates
        contactNames = list(set(contactNames))
        contactNames.sort()
        separator = "-"
        return separator.join(contactNames)
    
    @staticmethod
    def decodeParticipantID(encoded: str) -> list[str]:
        """
        Break a chat unique ID into a list of the contact names.
        """
        return encoded.split("-")

    def getUniqueID(self) -> str:
        """
        Returns the unique ID of this chat. This ID is created based on the chat
        participants.
        """
        return Chat.encodeParticipantID(self._participants)
    
    def getDisplayUniqueID(self) -> str:
        """
        Returns the unique ID of this chat. This ID is created based on the chat
        participants. This is for display purposes, IE, remove self from list.
        """
        l: list[str] = []
        for c in self._participants:
            if c != getpass.getuser():
                l.append(c)
        if not l:
            l.append(getpass.getuser())
        return Chat.encodeParticipantID(l)
    
    def getParticipants(self) -> list[str]:
        """
        Get the list of users participating in this Chat
        """
        return self._participants
    
    def updateMessageHistory(self, message: Message) -> None:
        """
        Adds a new message to message history and increases the number of unread
        messages.
        """
        self._history = [message] + self._history
        if message.getStatus == MessageStatus.UNREAD:
            self._numUnread += 1
        # Write to persistant storage
    
    def getMessageHistory(self) -> list[Message]:
        """
        Returns this Chat object's Message history as a list
        """
        return self._history
    
    def getMessageByDate(self, date: datetime) -> Message|None:
        """
        Gets the message based on the send date provided, or non if it does not
        exist.
        """
        for m in self._history:
            if m.getSent == date:
                return m
        return None
    
    def getNumUnread(self) -> int:
        """
        Returns the lumber of unread messages.
        """
        return self._numUnread
    
    def readMessages(self, number: int, start: int = 0) -> list[Message]:
        """
        Returns a list of n messages, starting from m. If any messages are
        marked as unread, mark them as read.
        """
        retVal: list[Message] = []
        for i in range(start, start+number):
            # Don't try to read past the end of messages
            if i >= len(self._history):
                break
            m: Message = self._history[i]
            retVal.append(m.copy())
            if m.getStatus() == MessageStatus.UNREAD:
                m.updateStatus(MessageStatus.READ)
                self._numUnread -= 1
        
        if self._numUnread < 0:
            self._numUnread = 0
        
        return retVal

    def getHeaderJsonObj(self) -> dict[str, object]:
        """
        Gets basic header info about the chat without the messages.
        """
        obj: dict[str, object] = self.toJsonObj()
        obj["history"] = []
        return obj

    def toJsonObj(self) -> dict[str, object]:
        """
        Turns this instance of Contact into a json compatable object.
        """
        jsonObj: dict[str, object] = {
            "numunread": self._numUnread,
            "participants" : self._participants,
            "history" : [m.toJsonObj() for m in self._history]
        }
        return jsonObj

    @staticmethod
    def fromJsonObj(jsonObj: object) -> 'Chat':
        """
        Returns a new Message from a provided json compatable object.
        """
        obj: dict[str, object] = cast(dict[str, object], jsonObj)
        chat: Chat = Chat(cast(list[str], obj["participants"]))
        chat._numUnread = cast(int, obj["numunread"])
        chat._history = [Message.fromJsonObj(m) for m in 
                         cast(list[Message], obj["history"])]
        return chat