from enum import Enum
import json
from typing import Any

class SPIT:
    """
    Simple Protocol for Information Transmission
    """
    class Type (Enum):
        """
        The type of SPIT
        """
        MESSAGE = 'message'
        STATUS = 'status'
        PING = 'ping'
    
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
            "data": self.data,
        })

    @staticmethod
    def fromString(spit: str) -> 'SPIT':
        """
        Takes a sent SPIT string and returns the SPIT object.
        """
        da: dict[str, Any] = json.loads(spit)
        return SPIT(SPIT.Type(da["type"]), da["data"])

