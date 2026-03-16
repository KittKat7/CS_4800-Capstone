import sys

from inbox import *
from filereader import *

args = sys.argv[1:]

match args[0]:
    case "ping":
        inbox: Inbox = Inbox()
        inbox.ping(Contact(args[1]))

    case "send":
        inbox: Inbox = Inbox()
        contact: Contact = Contact(args[1])
        message: Message = Message(args[2], "name")
        inbox.sendMessage(contact, DeliveryMessage(message, [], [contact]))

    case "inbox":
        Inbox.runInbox()

    case "online":
        inbox: Inbox = Inbox()
        isOnline: bool = inbox.ping(Contact(args[1]))
        print("User " + args[1] + " is online: " + str(isOnline))

    case "printdirs":
        _home = os.path.expanduser("~")
        xdg_data_home = os.environ.get("XDG_DATA_HOME") or \
            os.path.join(_home, ".local", "share")
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME") or \
            os.path.join(_home, ".config", "pytui")
        print("Data:", xdg_data_home, "Config:", xdg_config_home)

    case "store":
        # Currently only stores premade messages for demonstration purposes
        con = 'bob1235'
        con2 = 'jerrythesnail'
        match args[1]:
            case "1":
                mes = Message("hi", con)
                mes._status = MessageStatus(5)
                mes._sent = datetime.now()
                mes._recieved = datetime.now()
                dm = DeliveryMessage(mes, [], [con, con2])
                FileReader.storeMessage(dm)
            case "2":
                mes = Message("okay then", con)
                mes._status = MessageStatus(2)
                mes._sent = datetime.now()
                mes._recieved = datetime.now()
                dm = DeliveryMessage(mes, [con], [con, con2])
                FileReader.storeMessage(dm)
            case "3":
                mes = Message("bye", con)
                mes._status = MessageStatus(1)
                mes._sent = datetime.now()
                mes._recieved = datetime.now()
                dm = DeliveryMessage(mes, [con, con2], [con, con2])
                FileReader.storeMessage(dm)
    
    case "clear":
        # First demo message above will be cleared here
        FileReader.clearSent()

    case "makesettings":
        FileReader.makeSettings()

    case "getsetting":
        FileReader.getSetting(args[1])

    case "changesetting":
        FileReader.changeSetting(args[1], args[2])

    case "update":
        # Same demonstration messages as unsent storage
        con = 'bob1235'
        con2 = 'jerrythesnail'
        ch = Chat([con, con2])
        his = []
        unr = 0
        if len(args) > 1 and args[1] == "1":
            mes1 = Message('hi', con)
            mes1._status = MessageStatus(5)
            mes1._sent = datetime.now()
            mes1._recieved = datetime.now()
            his.append(mes1)
            unr += 1
        if len(args) > 2 and args[2] == "1":
            mes2 = Message('okay then', con)
            mes2._status = MessageStatus(2)
            mes2._sent = datetime.now()
            mes2._recieved = datetime.now()
            his.append(mes2)
            unr += 1
        if len(args) > 3 and args[3] == "1":
            mes3 = Message('goodbye', con)
            mes3._status = MessageStatus(1)
            mes3._sent = datetime.now()
            mes3._recieved = datetime.now()
            his.append(mes3)
            unr += 1
        ch._history = his
        ch._numUnread = unr
        FileReader.updateChat(ch)

    case "remove":
        con = 'bob1235'
        con2 = 'jerrythesnail'
        ch = Chat([con, con2])
        FileReader.removeChat(ch)

    case "get":
        con = 'bob1235'
        con2 = 'jerrythesnail'
        ch = Chat([con, con2])
        his = FileReader.getChat('bob1235jerrythesnail.json')
        if his == None:
            print("Chat not found")
        else:
            print(his.toJsonObj())

    case _:
        pass