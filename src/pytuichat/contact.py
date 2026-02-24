from enum import Enum

class ContactStatus(Enum):
    ONLINE  = 1
    AWAY    = 2
    OFFLINE = 3
    BLOCKED = 4

class Contact:
    def __init__(self):
        self._username: str
        self._displayname: str
        self._status: ContactStatus
        self._isBlocked: bool




