import json

class Settings:
    # Persist settings in a gardenSettings.json file
    def __init__(self):
        self._loadSettings()

    def _loadSettings(self):
        try:
            with open("settings.json", "r") as SettingsFile:
                self._settings = json.load(SettingsFile)
        except:
            self._settings = {}

    def getSSID(self):
        return self._settings.get("SSID","")

    def getPASSWORD(self):
        return self._settings.get("PASSWORD","")

    def getNTP(self):
        return self._settings.get("NTP","")

    def getPORT(self):
        return self._settings.get("PORT","37007")

    def getUSERS(self):
        return self._settings.get("USERS",[])