from enum import Enum
import json
from typing import Any

class SPIT:
    """
    Simple Protocol for Information Transmission
    Initial message is send with some form of data. Response message will be a
    STATUS type with a response code
    """
    class Type (Enum):
        """
        The type of SPIT
        """
        MESSAGE = 'message'
        STATUS = 'status'
        PING = 'ping'

    class Status (Enum):
        """
        Status codes for spits
        """
        OK = 200
        NOTFOUND = 404
        ERROR = 500
    
    def __init__(self, type: Type, data):
        """
        Constructor
        """
        self.type = type
        self.data = data

    def toString(self) -> str:
        """
        Turns the SPIT to a sendable string.
        """
        return json.dumps({
            "type": self.type.value,
            "data": self.data.value if self.type == SPIT.Type.STATUS else self.data
        })

    @staticmethod
    def fromString(spit: str) -> 'SPIT':
        """
        Takes a sent SPIT string and returns the SPIT object.
        """
        da: dict[str, Any] = json.loads(spit)
        t: SPIT.Type = SPIT.Type(da["type"])
        d: object = SPIT.Status(da["data"]) if t is SPIT.Type.STATUS else da["data"]
        return SPIT(t, d)

