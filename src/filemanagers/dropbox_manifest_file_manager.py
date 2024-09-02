import json
import os

from filemanagers.file_manager_base import FileManagerBase
from steam.steam_id import SteamId


class DropboxManifestFileManager(FileManagerBase):
    def __init__(self, steam_id: SteamId):
        filename = f'dropbox_{steam_id.get_steamid()}.json'
        super().__init__(filename=filename)


    def load_or_create_manifest(self):
        self._ensure_empty_file() 
        manifest = super().load_file()
        return manifest


    def save_manifest(self, manifest):
        return super().save_file(manifest)


    def _ensure_empty_file(self):
        file_path = self._get_file_path()
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump({}, f)
            print(f"Created new empty file: {file_path}")
