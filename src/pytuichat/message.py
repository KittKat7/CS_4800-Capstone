from datetime import datetime
from enum import Enum
from typing import cast

from contact import *

class MessageStatus(Enum):
    """
    The status of the message. This is used to mark the status of a message.
    """
    SENDING = 1
    SENT    = 2
    TIMEOUT = 3
    UNREAD  = 4
    READ    = 5

class Message:
    """
    A message which will be stored in a Chat.
    """
    def __init__(
    self,
    content: str,
    sender: str,
    status: MessageStatus = MessageStatus.UNREAD,
    sent: datetime = datetime.now(),
    recieved: datetime = datetime.now()):
        self._content: str = content
        self._status: MessageStatus = status
        self._sent: datetime = sent
        self._recieved: datetime = recieved
        self._sender: str = sender
        
    def updateStatus(self, status):
        self._status = status

    def updateContent(self, content):
        self._content = content
    
    def updateReceived(self, time):
        self._recieved = time
        
    def toJsonObj(self) -> object:
        """
        Turns this instance of Message into a json compatable object.
        """
        jsonObj: dict[str, object] = {
            "content": self._content,
            "status" : self._status.value,
            "sent": str(self._sent),
            "received" : str(self._recieved),
            "sender": self._sender
        }
        return jsonObj

    @staticmethod
    def fromJsonObj(jsonObj: object) -> 'Message':
        """
        Returns a new Message from a provided json compatable object.
        """
        obj: dict = cast(dict, jsonObj)
        message: Message = Message(
            content=obj["content"],
            sender=obj["sender"],
            status=MessageStatus(obj["status"]),
            sent=datetime.strptime(obj["sent"], f'%Y-%m-%d %H:%M:%S.%f'),
            recieved=datetime.strptime(obj["received"],  f'%Y-%m-%d %H:%M:%S.%f'))
        return message

class DeliveryMessage:
    """
    An object containing a Message and the info needed to send it. The extra
    information includes the list of participants in the chat and a list of
    contacts that still have not recieved the message. The sendingTo list
    contains the contacts that still need the message. Once a contact has
    recieved it, they are removed from the list. This list is also not passed to
    the recipient.
    """
    def __init__(self, message, sendingTo, recipients):
        """
        Constructor
        """
        self._message: Message = message
        self._sendingTo: list[str] = sendingTo
        self._recipients: list[str] = recipients

    def getMessage(self) -> Message:
        """
        Returns the message contained.
        """
        return self._message
    
    def getSendingTo(self) -> list[str]:
        """
        Returns a list of who still needs the message
        """
        return self._sendingTo

    def getRecipients(self) -> list[str]:
        """
        Returns the designated recipients of the message
        """
        return self._recipients

    def toJsonObj(self) -> dict:
        """
        Turns this instance of DeliveryMessage into a json compatable object.
        """
        jsonObj: dict[str, object] = {
            "message": self._message.toJsonObj(),
            "sendingTo": self._sendingTo,
            "recipients": self._recipients
        }
        return jsonObj

    @staticmethod
    def fromJsonObj(jsonObj: object) -> 'DeliveryMessage':
        """
        Returns a new DeliveryMessage from a provided json compatable object.
        """
        obj: dict = cast(dict, jsonObj)
        dmessage: DeliveryMessage = DeliveryMessage(
            Message.fromJsonObj(obj["message"]),
            obj["sendingTo"],
            obj["recipients"],
        )
        return dmessage