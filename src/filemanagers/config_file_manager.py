import os
import json
import sys
import tkinter as tk

from config.config_prompt_cli import ConfigPromptCli
from config.config_prompt_gui import ConfigPromptGui
from filemanagers.file_manager_base import FileManagerBase


class ConfigFileManager(FileManagerBase):
    ENCRYPTED_FIELDS = [
        'steam_api_key',
        'steamgriddb_api_key',
        'dropbox_app_key',
        'dropbox_app_secret',
        'dropbox_refresh_token',
        'nextcloud_passowrd'
    ]
    FILE_NAME = 'config.json'

    def __init__(self):
        super().__init__(filename=self.FILE_NAME, encryption_fields=self.ENCRYPTED_FIELDS)


    def load_or_create_preferences(self):
        config = super().load_file()
        if not config:
            config = self._prompt_user_for_config()
            super().save_file(config)
        return config


    def _prompt_user_for_config(self, use_gui=True):
        schema = self._get_config_schema()
        if use_gui:
            root = tk.Tk()
            config_prompt = ConfigPromptGui(root, schema)
            root.mainloop()
            root.destroy()
        else:
            config_prompt = ConfigPromptCli(root, schema)
        user_config = config_prompt.get_config()
        return user_config


    def _get_config_schema(self):
        schema_path = self._get_schema_path()
        with open(schema_path, 'r') as schema_file:
            schema = json.load(schema_file)
        return schema


    def _get_schema_path(self):
        # Check if running as a PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, 'config_schema.json')
        else:
            return 'config_schema.json'
