from datetime import datetime
from enum import Enum

from contact import *

class MessageStatus(Enum):
    SENDING = 1
    SENT    = 2
    TIMEOUT = 3
    UNREAD  = 4
    READ    = 5

class Message:
    def __init__(self):
        self._content: str
        self._status: MessageStatus
        self._sent: datetime
        self._recieved: datetime
        self._sender: Contact

class DeliveryMessage:
    def __init__(self):
        self._message: Message
        self._sendingTo: list[Contact]
        self.recipients: list[Contact]