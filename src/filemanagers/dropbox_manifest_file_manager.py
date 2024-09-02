from filemanagers.file_manager_base import FileManagerBase
from steam.steam_id import SteamID


class DropboxManifestFileManager(FileManagerBase):
    def __init__(self, steam_id: SteamID):
        filename = f'dropbox_{steam_id.get_steamid()}.json'
        super().__init__(filename=filename)


    def load_or_create_manifest(self):
        manifest = super().load_file()
        if not manifest:
            super().save_file(manifest)
        return manifest


    def save_manifest(self, manifest):
        return super().save_file(manifest)
