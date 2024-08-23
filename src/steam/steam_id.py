class SteamId:
    def __init__(self, steamid=None, steamid64=None, steamid3=None):
        if steamid:
            steamid = str(steamid)
            self.steamid64 = self._steamid_to_steamid64(steamid)
            self.steamid = steamid
            self.steamid3 = self._steamid64_to_steamid3(self.steamid64)
        elif steamid64:
            steamid64 = str(steamid64)
            self.steamid64 = steamid64
            self.steamid = self._steamid64_to_steamid(steamid64)
            self.steamid3 = self._steamid64_to_steamid3(steamid64)
        elif steamid3:
            steamid3 = str(steamid3)
            self.steamid64 = self._steamid3_to_steamid64(steamid3)
            self.steamid = self._steamid64_to_steamid(self.steamid64)
            self.steamid3 = steamid3
        else:
            raise ValueError("A steamid, steamid64 or steamid3 must be provided.")

    def _steamid64_to_steamid(self, steamid64):
        steamid = str(int(steamid64) - 76561197960265728)
        return steamid

    def _steamid_to_steamid64(self, steamid):
        steamid64 = str(int(steamid) + 76561197960265728)
        return steamid64

    def _steamid64_to_steamid3(self, steamid64):
        steamid = self._steamid64_to_steamid(self, steamid64)
        steamid3 = "[U:1:" + str(steamid) + "]"
        return steamid3

    def _steamid3_to_steamid64(self, steamid3):
        steamid = steamid3.split(":")[2][:-1]
        steamid64 = self._steamid_to_steamid64(steamid)
        return steamid64
    
    def get_steamid(self):
        return self.steamid

    def get_steamid64(self):
        return self.steamid64

    def get_steamid3(self):
        return self.steamid3

    def __str__(self):
        return f"SteamID: {self.steamid}, SteamID64: {self.steamid64}, SteamID3: {self.steamid3}"
