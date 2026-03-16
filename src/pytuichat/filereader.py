import os
import json
from chat import *

class FileReader:
    @staticmethod
    def makeSettings():
        """
        Makes the necessary folder for the settings and adds the settings to it.
        """
        defaults = {'show_nicknames' : 'yes',
                    'highlight_color' : 'yellow',
                    'sort_by' : 'most_recent_message',
                    'confirm_deletion' : 'yes'
                    }
        
        title = "settings.json"
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_CONFIG_HOME") or \
                os.path.join(_home, ".config","pytui")
        full_path = os.path.join(dir_path, title)
        os.makedirs(os.path.dirname(full_path), exist_ok = True)
        try:
            with open(full_path, 'w') as f:
                json.dump(defaults, f, indent=4)
        except FileExistsError:
            print(full_path, "already exists")
        except Exception as e:
            print('Error:\n', e)

    @staticmethod
    def getSetting(setting : str) -> str:
        """
        Returns a string representing the current value of setting in the
        settings file, or "" if an error occurs.
        """
        title = "settings.json"
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_CONFIG_HOME") or \
                os.path.join(_home, ".config","pytui")
        full_path = os.path.join(dir_path, title)
        try:
            with open(full_path, "r") as f:
                settings = json.load(f)
                output = settings[setting]
                f.close()
                return output
        except FileNotFoundError:
            print(full_path, "was not found")
            return ""
        except Exception as e:
            print("Error:\n", e, sep="")
            return ""

    @staticmethod
    def changeSetting(setting : str, new : str) -> bool:
        """
        Changes the value of setting in the settings file to new.
        Returns True if the update was successful or False if an error occured.
        """
        title = "settings.json"
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_CONFIG_HOME") or \
                os.path.join(_home, ".config","pytui")
        full_path = os.path.join(dir_path, title)
        try:
            with open(full_path, "r") as f:
                settings = json.load(f)
                settings[setting] = new
                f.close()
                json.dump(settings, open(full_path, "w"), indent=4)
                return True
        except FileNotFoundError:
            print(full_path, "was not found")
            return False
        except Exception as e:
            print("Error:\n", e, sep="")
            return False

    @staticmethod
    def updateChat(chat : Chat):
        """
        Create a new JSON file in the pytui local data folder or update an
        existing one. The file will be a JSON representation of the given Chat.
        """
        # Might be best to come up with a more concise title convention
        # This will do for now, though
        title = ""
        for user in chat.getParticipants():
            title += user
        title += ".json"
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_DATA_HOME") or \
                os.path.join(_home, '.local', 'share', "pytui")
        full_path = os.path.join(dir_path, title)
        os.makedirs(os.path.dirname(full_path), exist_ok = True)
        with open(full_path, 'w') as f:
            json.dump(chat.toJsonObj(), f, indent=4)

    @staticmethod
    def removeChat(chat : Chat):
        """
        Removes the JSON file representing the given Chat from the pytui local
        data folder. Does nothing if the JSON file does not exist.
        """
        title = ""
        for user in chat.getParticipants():
            title += user
        title += ".json"
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_DATA_HOME") or \
                os.path.join(_home, '.local', 'share', "pytui")
        full_path = os.path.join(dir_path, title)
        try:
            os.remove(full_path)
        except FileNotFoundError:
            print(full_path, "was not found")

    @staticmethod
    def getChat(title : str) -> Chat:
        """
        Returns Chat object represented by the json file with the given title.
        TODO need a way to actually get the titles
        # """
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_DATA_HOME") or \
                os.path.join(_home, '.local', 'share', "pytui")
        full_path = os.path.join(dir_path, title)
        try:
            with open(full_path, "r") as f:
                return Chat.fromJsonObj(json.load(f))
        except FileNotFoundError:
            raise Exception(f"The file {full_path} was not found")

    @staticmethod
    def storeMessage(dmessage : DeliveryMessage):
        """
        Store a DelivaryMessage that has not been received to reattempt sending 
        at a later time.
        """
        title = ".unsent.json"
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_DATA_HOME") or \
                os.path.join(_home, '.local', 'share', "pytui")
        full_path = os.path.join(dir_path, title)
        if os.path.isfile(full_path):
            # Add the DeliveryMessage to the .unsent file
            with open(full_path, "r") as f:
                unsentList = json.load(f)
                unsentList.append(dmessage.toJsonObj())
                f.close()
                json.dump(unsentList, open(full_path, "w"), indent=4)
        else:
            # Create a new .unsent file with a list containing the DeliveryMessage
            json.dump([dmessage.toJsonObj()], open(full_path, "w"), indent=4)

    @staticmethod
    def clearSent():
        """
        Removes all DeliveryMessages with empty sendingTo lists.
        """
        title = ".unsent.json"
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_DATA_HOME") or \
                os.path.join(_home, '.local', 'share', "pytui")
        full_path = os.path.join(dir_path, title)
        try:
            with open(full_path, "r") as f:
                unsentList = json.load(f)
                targets = []
                for i in range(0, len(unsentList)):
                    if len(unsentList[i]["sendingTo"]) < 1:
                        targets.append(i)
                for t in reversed(targets):
                    unsentList.pop(t)
                f.close()
                json.dump(unsentList, open(full_path, "w"), indent=4)
        except FileNotFoundError:
            # If there is no .unsent, no messages to clear
            pass
        except Exception as e:
            print("Error:\n", e, sep="")

    @staticmethod
    def getUnsent() -> list[DeliveryMessage]:
        """
        Returns a list containing all DeliveryMessages in .unsent.json. Will
        include those that have empty sendingTo lists. Call clearSent() first or
        filter the output list if this behavior is undesirable.
        """
        title = ".unsent.json"
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_DATA_HOME") or \
                os.path.join(_home, '.local', 'share', "pytui")
        full_path = os.path.join(dir_path, title)
        try:
            with open(full_path, "r") as f:
                dms = []
                unsentList = json.load(f)
                for dm in unsentList:
                    dms.append(DeliveryMessage.fromJsonObj(dm))
                return dms
        except FileNotFoundError:
            return []