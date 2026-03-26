import os
import json
from chat import *

class FileReader:
    # Used for debugging
    isDebug: bool

    @staticmethod
    def setDebug(debug: bool):
        """
        Sets the debug flag. Actual debug flag functionality is WIP.
        """
        FileReader.isDebug = debug

    @staticmethod
    def getConfigDir() -> str:
        """
        Returns the path to the directory config files will be stored in.
        """
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_CONFIG_HOME") or \
                os.path.join(_home, ".config", "pytui")
        return dir_path
    
    @staticmethod
    def getDataDir() -> str:
        """
        Returns the path to the directory user data files will be stored in.
        """
        _home = os.path.expanduser("~")
        dir_path = os.environ.get("XDG_DATA_HOME") or \
                os.path.join(_home, ".local", "share", "pytui")
        return dir_path

    @staticmethod
    def getChatTitles() -> list[str]:
        """
        Returns the titles of all JSON Chat logs in the pytui local data folder.
        Ignores non-JSON files and the unique .unsent.json
        """
        dir_path = FileReader.getDataDir()
        return [f for f in os.listdir(dir_path) if 
                f not in [".unsent.json", ".contacts.json"] and 
                f[-5:] == ".json"]

    @staticmethod
    def makeSettings():
        """
        Makes the necessary folder for the settings and adds the settings to it.
        """
        defaults = {"show_nicknames" : "yes",
                    "highlight_color" : "yellow",
                    "sort_by" : "most_recent_message",
                    "confirm_deletion" : "yes"
                    }
        
        title = "settings.json"
        dir_path = FileReader.getConfigDir()
        full_path = os.path.join(dir_path, title)
        os.makedirs(os.path.dirname(full_path), exist_ok = True)
        try:
            with open(full_path, "w") as f:
                json.dump(defaults, f, indent=4)
        except Exception as e:
            print("Error:\n", e, sep="")
            
    @staticmethod
    def getSettings() -> dict[str, str]:
        """
        Returns a dict representing the user's list of settings. If the file
        doesn't exist, create it and populate with the default settings.
        """
        title = "settings.json"
        dir_path = FileReader.getConfigDir()
        full_path = os.path.join(dir_path, title)
        if not os.path.isfile(full_path):
            FileReader.makeSettings()
        with open(full_path, "r") as f:
            settings = json.load(f)
            return settings

    @staticmethod
    def updateSettings(settings: dict[str, str]):
        """
        Updates the settings file with new values.
        """
        title = "settings.json"
        dir_path = FileReader.getConfigDir()
        full_path = os.path.join(dir_path, title)
        if not os.path.isfile(full_path):
            FileReader.makeSettings()
        try:
            with open(full_path, "w") as f:
                json.dump(settings, f)
        except FileNotFoundError:
            print(full_path, "was not found")

    @staticmethod
    def updateContacts(con: dict[str, Contact]):
        """
        Create/update .contacts.json file with a list of the user's contacts.
        """
        title = ".contacts.json"
        dir_path = FileReader.getDataDir()
        full_path = os.path.join(dir_path, title)
        with open(full_path, "w") as f:
            contacts: list[object] = []
            for c in con.values():
                contacts.append(c.toJsonObj())
            f.close()
            json.dump(contacts, open(full_path, "w"), indent=4)
    
    @staticmethod
    def getContacts() -> dict[str, Contact]:
        """
        Returns a list containing all contacts stored in .contacts.json.
        """
        contacts: dict[str, Contact] = {}
        title = ".contacts.json"
        dir_path = FileReader.getDataDir()
        full_path = os.path.join(dir_path, title)
        with open(full_path, "r") as f:
            for c in json.load(f):
                con = Contact.fromJsonObj(c)
                contacts[con.getUsername()] = con
        return contacts
    
    @staticmethod
    def updateChat(chat: Chat):
        """
        Create a new JSON file in the pytui local data folder or update an
        existing one. The file will be a JSON representation of the given Chat.
        """
        title = Chat.encodeParticipantID(chat.getParticipants()) + ".json"
        dir_path = FileReader.getDataDir()
        full_path = os.path.join(dir_path, title)
        os.makedirs(os.path.dirname(full_path), exist_ok = True)
        with open(full_path, "w") as f:
            json.dump(chat.toJsonObj(), f, indent=4)

    @staticmethod
    def removeChat(chat: Chat):
        """
        Removes the JSON file representing the given Chat from the pytui local
        data folder. Does nothing if the JSON file does not exist.
        """
        title = Chat.encodeParticipantID(chat.getParticipants()) + ".json"
        dir_path = FileReader.getDataDir()
        full_path = os.path.join(dir_path, title)
        try:
            os.remove(full_path)
        except FileNotFoundError:
            print(full_path, "was not found.")

    @staticmethod
    def getChat(title: str) -> Chat:
        """
        Returns Chat object represented by the json file with the given title.
        # """
        dir_path = FileReader.getDataDir()
        full_path = os.path.join(dir_path, title)
        try:
            with open(full_path, "r") as f:
                return Chat.fromJsonObj(json.load(f))
        except FileNotFoundError:
            raise FileNotFoundError(full_path, "was not found.")

    @staticmethod
    def updateUnsentList(messages: list[DeliveryMessage]):
        """
        Store a list of DelivaryMessages that have not been received to 
        reattempt sending at a later time. Replaces existing list if it exists.
        """
        title = ".unsent.json"
        dir_path = FileReader.getDataDir()
        full_path = os.path.join(dir_path, title)
        with open(full_path, "w") as f:
            unsentList: list[object] = []
            for dm in messages:
                unsentList.append(dm.toJsonObj())
            json.dump(unsentList, f, indent=4)

    @staticmethod
    def getUnsent() -> list[DeliveryMessage]:
        """
        Returns a list containing all DeliveryMessages in .unsent.json. Will
        include those that have empty sendingTo lists. Call clearSent() first or
        filter the output list if this behavior is undesirable. If .unsent.json
        does not exist, returns an empty list.
        """
        title = ".unsent.json"
        dir_path = FileReader.getDataDir()
        full_path = os.path.join(dir_path, title)
        try:
            with open(full_path, "r") as f:
                dms: list[DeliveryMessage] = []
                unsentList = json.load(f)
                for dm in unsentList:
                    dms.append(DeliveryMessage.fromJsonObj(dm))
                return dms
        except FileNotFoundError:
            return []