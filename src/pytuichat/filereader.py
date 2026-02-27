import json

from chat import *

# Should return a string representing the current value of setting in the settings file
# TODO
def getSetting(setting):
    pass

# Should change the value of setting in the settings file
# TODO
def changeSetting(setting, new):
    pass

# Should create a new conversation in chats.json with everyone in users
# Should also create a new file for that chat (figure out how to name group chats)
# Should start with 0 unread messages
# TODO
def addChat(users):
    pass

# Should remove the specified chat from chats.json, and remove the json specific to that chat
# Will most likely be used when blocking users?
# TODO
def removeChat(title):
    pass

# Should return all messages from the json for the specified chat
# Need to do so in a format that lets the front end display them to the user
# TODO
def dumpChat(title):
    pass

# Should add the given message to the specified chat
# If isRead, set unread messages for the specified chat to 0 in chats.json
# If not, increment unread messages
# New message may be None, if only want to mark chat as read
def updateChat(title, message, isRead):
    pass