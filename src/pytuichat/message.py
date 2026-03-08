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
    sender: Contact,
    status: MessageStatus = MessageStatus.UNREAD,
    sent: datetime = datetime.now(),
    recieved: datetime = datetime.now()):
        self._content: str = ""
        self._status: MessageStatus
        self._sent: datetime
        self._recieved: datetime
        self._sender: Contact

    def toJsonObj(self) -> object:
        """
        Turns this instance of Message into a json compatable object.
        """
        jsonObj: dict[str, object] = {
            "content": self._content,
            "status" : self._status,
            "sent": self._sent,
            "received" : self._recieved,
            "sender": self._sender
        }
        return jsonObj

    @staticmethod
    def fromJsonObj(jsonObj: object) -> 'DeliveryMessage':
        """
        Returns a new Message from a provided json compatable object.
        """
        obj: dict = cast(dict, jsonObj)
        message: Message = Message(
            content=obj["content"],
            sender=obj["sender"],
            status=obj["status"],
            sent=obj["sent"],
            recieved=obj["received"])
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
        self._message: Message
        self._sendingTo: list[Contact]
        self._recipients: list[Contact]

    def getMessage(self) -> Message:
        """
        Returns the message contained.
        """
        return self._message
    
    def getSendingTo(self) -> list[Contact]:
        """
        Returns a list of who still needs the message
        """
        return self._sendingTo

    def getRecipients(self) -> list[Contact]:
        """
        Returns the designated recipients of the message
        """
        return self._recipients

    def toJsonObj(self) -> object:
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
            obj["message"],
            obj["sendingTo"],
            obj["recipients"]
        )
        return dmessage