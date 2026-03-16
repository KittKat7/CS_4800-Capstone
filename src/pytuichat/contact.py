from enum import Enum
from typing import cast

class ContactStatus(Enum):
    ONLINE  = 1
    AWAY    = 2
    OFFLINE = 3
    BLOCKED = 4

class Contact:
    def __init__(self, username: str):
        self._username: str = username
        self._displayname: str = ""
        self._status: ContactStatus = ContactStatus.ONLINE
        # TODO _isBlocked is repetative as their status can be blocked
        self._isBlocked: bool = False
    
    def getUsername(self) -> str:
        return self._username

    def toJsonObj(self) -> object:
        """
        Turns this instance of Contact into a json compatable object.
        """
        jsonObj: dict[str, object] = {
            "username": self._username,
            "displayname" : self._displayname,
            "status" : self._status.value,
            "isBlocked" : self._isBlocked
        }
        return jsonObj

    @staticmethod
    def fromJsonObj(jsonObj: object) -> 'Contact':
        """
        Returns a new Message from a provided json compatable object.
        """
        obj: dict[str, object] = cast(dict[str, object], jsonObj)
        contact: Contact = Contact(cast(str, obj["username"]))
        contact._displayname = cast(str, obj["displayname"])
        contact._status = ContactStatus(obj["status"])
        contact._isBlocked = cast(bool, obj["isBlocked"])
        return contact