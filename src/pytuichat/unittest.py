import unittest
from filereader import *

class TestMessageIO(unittest.TestCase):
    @staticmethod
    def testStartInbox() -> None:
        """
        """

class TestFileIO(unittest.TestCase):
    # TODO implement literally all of this
    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()
    
    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()
    
    def testSettings(self):
        """
        Test the functions relevant to the settings file.
        """
        self.assertTrue(True)
            
    def testContactList(self):
        """
        Test the functions relevant to the stored list of Contacts.
        """
        self.assertTrue(True)
    
    def testUnsent(self):
        """
        Test the functions relevant to the stored list of unsent Messages.
        """
        self.assertTrue(True)
    
    def testHistory(self):
        """
        Test the functions relevant to the storage of Message history.
        """
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()