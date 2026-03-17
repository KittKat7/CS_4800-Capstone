
from message import *
from contact import *
from typing import cast

class Chat:
    def __init__(self, contacts: list[str]):
        self._numUnread: int = 0
        self._participants: list[str] = contacts
        self._history: list[Message] = []
    
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
        self._numUnread += 1
        print("Update persist messages")
        # TODO save persistant
    
    def getMessageHistory(self) -> list[Message]:
        """
        """
        # TODO
        return self._history

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