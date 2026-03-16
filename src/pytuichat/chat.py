
from message import *
from contact import *
from typing import cast

class Chat:
    def __init__(self, contacts):
        self._numUnread: int = 0
        self._participants: list[Contact] = contacts
        self._history: list[Message] = []
    
    def updateMessageHistory(self, Message) -> None:
        """
        Adds a new message to message history and increases the number of unread
        messages.
        """
        self._history = [Message] + self._history
        self._numUnread += 1
        print("Update persist messages")
        # TODO save persistant
    
    def getMessageHistory(self) -> list[Message]:
        """
        """
        # TODO
        return self._history

    def toJsonObj(self):
        """
        Turns this instance of Contact into a json compatable object.
        """
        jsonObj: dict[str, object] = {
            "numunread": self._numUnread,
            "participants" : [p.toJsonObj() for p in self._participants],
            "history" : [m.toJsonObj() for m in self._history]
        }
        return jsonObj

    @staticmethod
    def fromJsonObj(jsonObj: object) -> 'Chat':
        """
        Returns a new Message from a provided json compatable object.
        """
        obj: dict = cast(dict, jsonObj)
        chat: Chat = Chat([Contact.fromJsonObj(p) for p in obj["participants"]])
        chat._numUnread = obj["numunread"]
        chat._history = [Message.fromJsonObj(m) for m in obj["history"]]
        return chat