# Interface Data In-Out Transport
from enum import Enum
import json

class IDIOT_TYPE(Enum):
    STOP = -1
    PING = 1
    SEND = 2
    RECIEVE = 3
    GETCH = 4

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