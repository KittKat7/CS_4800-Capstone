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
    def __init__(self):
        self._content: str
        self._status: MessageStatus
        self._sent: datetime
        self._recieved: datetime
        self._sender: Contact

class DeliveryMessage:
    """
    An object containing a Message and the info needed to send it. The extra
    information includes the list of participants in the chat and a list of
    contacts that still have not recieved the message. The sendingTo list
    contains the contacts that still need the message. Once a contact has
    recieved it, they are removed from the list. This list is also not passed to
    the recipient.
    """
    def __init__(self):
        """
        Constructor
        """
        self._message: Message
        self._sendingTo: list[Contact]
        self._recipients: list[Contact]

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

    def fromJsonObj(jsonObj: object) -> 'DeliveryMessage':
        """
        Returns a new DeliveryMessage from a provided json compatable object.
        """
        obj: dict = cast(dict, jsonObj)
        dmessage: DeliveryMessage = DeliveryMessage()
        dmessage._message = obj["message"]
        dmessage._sendingTo = obj["sendingTo"]
        dmessage._recipients = obj["recipients"]
        return dmessage