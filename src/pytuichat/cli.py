import sys

from inbox import *

args = sys.argv[1:]

match args[0]:
    case "ping":
        inbox: Inbox = Inbox()
        inbox.ping(Contact(args[1]))

    case "send":
        inbox: Inbox = Inbox()
        contact: Contact = Contact(args[1])
        message: Message = Message(args[2], Contact("name"))
        inbox.sendMessage(contact, DeliveryMessage(message, [], [contact]))

    case "inbox":
        Inbox.runInbox()

    case "online":
        inbox: Inbox = Inbox()
        isOnline: bool = inbox.ping(Contact(args[1]))
        print("User " + args[1] + " is online: " + str(isOnline))
