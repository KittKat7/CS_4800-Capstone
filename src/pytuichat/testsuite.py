import unittest

from .filereader import *
from .inbox import Inbox
from .message import DeliveryMessage, Message
from .contact import Contact

class TestMessageIO(unittest.TestCase):
    def testSendMessage(self):
        """
        Tests that send message adds the message into the inbox's outbox.
        """
        Inbox.runInbox(isDebug=True)
        Inbox._outbox = [] #type: ignore
        self.assertTrue(Inbox._outbox == []) # type: ignore
        dm = DeliveryMessage(
            Message(
                "TestMSG",
                "Bob"
            ),
            ["jim"],
            "1234"
        )
        Inbox._sendMessage( #type: ignore
            dm
        )
        self.assertTrue(Inbox._outbox == []) # type: ignore
        self.assertTrue(debug.message == [dm]) # type: ignore


class TestFileIO(unittest.TestCase):
    # TODO should store temp copies of the files
    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()
    # TODO should restore the temp copies of the files to their locations
    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()
    
    def testMakeSettings(self):
        """
        Test that makeSettings() initializes the settings file with the correct
        default values.
        """
        defaults = {
                    "show_nicknames" : True,
                    "24_hour_time" : False
                    }
        FileReader.makeSettings()
        settings = FileReader.getSettings()
        self.assertTrue(settings[k] == defaults[k] for k in defaults.keys())

    def testUpdateSettings(self):
        """
        Test that updateSettings correctly changes the value of the settings in
        the file.
        """
        settings = {
                    "show_nicknames" : True,
                    "24_hour_time" : False
                    }
        # Reset settings to their defaults first
        FileReader.makeSettings()
        FileReader.updateSettings(settings)
        self.assertTrue(FileReader.getSettings() == settings)
            
    def testContactList(self):
        """
        Test the functions relevant to the stored list of Contacts.
        """
        contacts = {"bob1235" : Contact("bob1235"), 
                    "jerrythesnail" : Contact("jerrythesnail")}
        FileReader.updateContacts(contacts)
        storedContacts = FileReader.getContacts()
        self.assertTrue(contacts[i].toJsonObj() == storedContacts[i].toJsonObj()
                         for i in contacts.keys())
    
    def testUnsent(self):
        """
        Test the functions relevant to the stored list of unsent Messages.
        """
        mes1 = Message("Hi there", "bob1235", MessageStatus.UNREAD)
        mes2 = Message("Hello!", "jerrythesnail", MessageStatus.SENT)
        dm1 = DeliveryMessage(mes1, [], "a")
        dm2 = DeliveryMessage(mes2, ["bob1235"], "a")
        dms = [dm1, dm2]
        FileReader.updateUnsentList([dm1, dm2])
        storeddms = FileReader.getUnsent()
        self.assertTrue(dms[i].toJsonObj() == storeddms[i].toJsonObj()
                         for i in range(0, 2))
    
    def testHistory(self):
        """
        Test that files representing Chats can be successfully stored and read.
        """
        ch = Chat(["bob1235", "jerrythesnail"])
        mes1 = Message("Hi there", "bob1235", MessageStatus.UNREAD)
        mes2 = Message("Hello!", "jerrythesnail", MessageStatus.SENT)
        ch.updateMessageHistory(mes1)
        ch.updateMessageHistory(mes2)
        FileReader.updateChat(ch)
        title = Chat.encodeParticipantID(["bob1235", "jerrythesnail"]) + ".json"
        storedch = FileReader.getChat(title)
        self.assertTrue(ch.toJsonObj() == storedch.toJsonObj())
    
    def testRemoval(self):
        """
        Ensure that Chats can be removed from the local files, and that an
        exception is correctly thrown when trying to access one that does not
        exist.
        """
        ch = Chat(["bob1235", "jerrythesnail"])
        FileReader.updateChat(ch)
        FileReader.removeChat(ch)
        title = Chat.encodeParticipantID(["bob1235", "jerrythesnail"]) + ".json"
        with self.assertRaises(FileNotFoundError):
            FileReader.getChat(title)

if __name__ == "__main__":
    unittest.main()