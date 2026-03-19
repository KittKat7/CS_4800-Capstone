import unittest

from inbox import Inbox
from message import DeliveryMessage, Message
from contact import Contact

class TestMessageIO(unittest.TestCase):

    def testSendMessage(self):
        """
        Tests that send message adds the message into the inbox's outbox.
        """
        ib = Inbox()

        self.assertTrue(ib._outbox == []) # type: ignore

        dm = DeliveryMessage(
            Message(
                "TestMSG",
                "Bob"
            ),
            ["jim"],
            "1234"
        )
        ib.sendMessage(
            Contact("jim"),
            dm
        )

        self.assertTrue(ib._outbox == [dm]) # type: ignore



if __name__ == "__main__":
    unittest.main()