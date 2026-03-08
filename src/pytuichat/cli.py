import sys

from inbox import *

args = sys.argv[1:]

match args[0]:
    case "send":
        inbox: Inbox = Inbox()
        contact: Contact = Contact(args[1])
        message: Message = Message(args[2], "testing")
        inbox.sendMessage(contact, DeliveryMessage(message, [], [contact]))

    case "inbox":
        Inbox.runInbox()

    case "online":
        inbox: Inbox = Inbox()
        isOnline: bool = inbox.isContactSendable(Contact(args[1]))
        print("User " + args[1] + " is online: " + str(isOnline))
