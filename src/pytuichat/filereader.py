import os
import json
from chat import *

# Makes the necessary folder for the settings and adds the settings to it
# TODO test this
def makeSettings():
    _home = os.path.expanduser('~')
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or \
            os.path.join(_home, '.config')
    
    try:
        # TODO finish converting this to nested directory
        os.makedirs(os.path.join(settingsLoc, 'pytui'))
    except FileExistsError:
        # No need to make a new folder if it already exists
        pass
    except Exception as e:
        print('Error:\n', e)
    settingsLoc = os.path.join(settingsLoc, 'pytui')
    # TODO remove this, it's only gonna be here for testing purposes
    print(settingsLoc)
    # TODO make this write the default settings to the created file
    defaults = {'show_nicknames' : 'yes',
                'highlight_color' : 'yellow',
                'sort_by' : 'most_recent_message',
                'confirm_deletion' : 'yes'
                }
    f = open(f'{settingsLoc}/settings.json', 'w')
    json.dump(defaults, f)
    f.close()

# Should return a string representing the current value of setting in the settings file
# TODO test this
def getSetting(setting):
    settingsLoc = os.environ.get('XDG_CONFIG_HOME').join('/pytui/settings.json')
    f = open(settingsLoc)
    settings = json.load(f)
    output = settings[setting]
    f.close()
    return output

# Should change the value of setting in the settings file
# TODO
def changeSetting(setting, new):
    settingsLoc = os.environ.get('XDG_CONFIG_HOME').join('/pytui/settings.json')
    f = open(settingsLoc)
    settings = json.load(f)
    settings[setting] = new
    json.dump(settings, settingsLoc)
    f.close()

# Create a new conversation in the pytui local data folder or update an existing one
# The new conversation will be based on the given Chat object
def updateChat(chat):
    # Might be best to come up with a more concise title convention
    # This will do for now, though
    title = ""
    for user in chat._participants:
        title += user.getUsername()
    title += ".json"
    _home = os.path.expanduser("~")
    dir_path = os.environ.get("XDG_DATA_HOME") or \
            os.path.join(_home, '.local', 'share', "pytui")
    full_path = os.path.join(dir_path, title)
    os.makedirs(os.path.dirname(full_path), exist_ok = True)
    with open(full_path, 'w') as f:
        json.dump(chat.toJsonObj(), f)

# Should remove json file representing the given Chat object
# Will most likely be used when blocking users
def removeChat(chat):
    title = ""
    for user in chat._participants:
        title += user.getUsername()
    title += ".json"
    _home = os.path.expanduser("~")
    dir_path = os.environ.get("XDG_DATA_HOME") or \
            os.path.join(_home, '.local', 'share', "pytui")
    full_path = os.path.join(dir_path, title)
    try:
        os.remove(full_path)
    except FileNotFoundError:
        print(full_path, "was not found")
    except Exception as e:
        print("Error:\n", e, sep="")

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