
from message import *
from contact import *
from typing import cast

class Chat:
    def __init__(self):
        self._numUnread: int
        self._participants: list[Contact]
        self._history: list[Message]
    
    def updateMessageHistory(self, Message) -> None:
        """
        """
        # TODO
    
    def getMessageHistory(self) -> list[Message]:
        """
        """
        # TODO
        return self._history

    def toJsonObj(self):
        """
        Turns this instance of Contact into a json compatable object.
        """
        # TODO currently gives an error stating:
        # 'Message' object has no attribute '_sender'
        # Needs to be fixed
        jsonObj: dict[str, object] = {
            "numunread": self._numUnread,
            "participants" : [p.toJsonObj() for p in self._participants],
            "history" : [m.toJsonObj() for m in self._history]
        }
        return jsonObj

    def fromJsonObj(jsonObj: object) -> 'Chat':
        """
        Returns a new Message from a provided json compatable object.
        """
        obj: Chat = cast(dict, jsonObj)
        chat: Chat = Chat()
        chat._numUnread = obj["numunread"]
        chat._participants = obj["participants"]
        chat._history = obj["history"]
        return chat