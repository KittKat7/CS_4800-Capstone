from filereader import FileReader

class SettingsManager:

    _instance: 'SettingsManager | None' = None

    @staticmethod
    def getSettingsManager() -> 'SettingsManager':
        """
        Returns an existing, or makes a new instance of SettingsManager.
        """
        if not SettingsManager._instance:
            SettingsManager._instance = SettingsManager()
        return SettingsManager._instance

    def __init__(self):
        """
        Constructor.
        """
        userSettings = FileReader.getSettings()
        try:
            self._showNicknames = userSettings["show_nicknames"]
            self._24Hour = userSettings["24_hour_time"]
        except Exception:
            # Triggers if the user's setting file is missing an entry
            FileReader.makeSettings()
            userSettings = FileReader.getSettings()
            self._showNicknames = userSettings["show_nicknames"]
            self._24Hour = userSettings["24_hour_time"]

    def getShowNicknames(self) -> bool:
        """
        Returns the value of showNicknames.
        """
        return self._showNicknames
    
    def get24Hour(self) -> bool:
        """
        Returns the value of 24Hour.
        """
        return self._24Hour
    
    def setShowNicknames(self, val: bool):
        """
        Changes the show nicknames setting to the new value val.
        """
        self._showNicknames = val

    def set24Hour(self, val: bool):
        """
        Changes the 24 hour time setting to the new value val.
        """
        self._24Hour = val