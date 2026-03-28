# Interface Data In-Out Transport
from enum import Enum
import json

class IDIOT_TYPE(Enum):
    # Stop the program
    STOP = -1
    # Ping the inbox to make sure its running
    PING = 1
    # Send a message
    SEND_MSG = 2
    # Get a chat
    GET_CHAT = 3
    # Get contacts
    GET_CONTACTS = 4

class IDIOT:
    def __init__(self, type: IDIOT_TYPE, data: object):
        self.type = type
        self.data = data

    def toString(self) -> str:
        """
        Turns the IDIOT to a sendable string.
        """
        return json.dumps({
            "type": self.type.value,
            "data": self.data
        })

    @staticmethod
    def fromString(idiot: str) -> 'IDIOT':
        """
        Takes a sent IDIOT string and returns the IDIOT object.
        """
        da: dict[str, object] = json.loads(idiot)
        t: IDIOT_TYPE = IDIOT_TYPE(da["type"])
        d: object = da["data"]
        return IDIOT(t, d)