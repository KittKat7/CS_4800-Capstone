from message import *
from contact import *
from chat import *

class Inbox:
    def __init__(self):
        self._contacts: list[str]
        self._chats: list[Chat]
    
    def getChats(self) -> list[Chat]:
        return self._chats
    
    def sendMessage(self, contact: Contact, message: Message) -> None:
        """
        """
        # TODO
    
    def isContactSendable(self, contact: Contact) -> bool:
        """
        """
        # TODO

    def _deliverMessage(self, contact: Contact, message: Message) -> bool:
        """
        """
        # TODO
    
    def _onMessageRecieved(self, message: Message) -> None:
        """
        """
        # TODO




