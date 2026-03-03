from enum import Enum
from typing import cast

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

    def toJsonObj(self) -> object:
        """
        Turns this instance of Contact into a json compatable object.
        """
        jsonObj: dict[str, object] = {
            "username": self._username,
            "displayname" : self._displayname,
            "status" : self._status,
            "isBlocked" : self._isBlocked
        }
        return jsonObj

    def fromJsonObj(jsonObj: object) -> 'Contact':
        """
        Returns a new Message from a provided json compatable object.
        """
        obj: dict = cast(dict, jsonObj)
        contact: Contact = Contact()
        contact._username = obj["username"]
        contact._displayname = obj["displayname"]
        contact._status = obj["status"]
        contact._isBlocked = obj["isBlocked"]
        return contact