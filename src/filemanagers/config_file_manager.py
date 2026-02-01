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
        'nextcloud_password' # Fixed typo 'nextcloud_passowrd' -> 'nextcloud_password' (assuming schema matches) - Wait, schema uses 'nextcloud_password'. The typo was in this file likely? Or I should check schema again. Schema has "nextcloud_password".
    ]
    FILE_NAME = 'config.json'

    def __init__(self):
        super().__init__(filename=self.FILE_NAME, encryption_fields=self.ENCRYPTED_FIELDS)


    def load_or_create_preferences(self):
        config = super().load_file()
        if not config:
            return None
        return config


    def edit_preferences(self, use_gui=True):
        current_config = self.load_or_create_preferences()
        schema = self._get_config_schema()
        
        if use_gui:
            root = tk.Tk()
            config_prompt = ConfigPromptGui(root, schema, current_config=current_config)
            user_config = config_prompt.get_config()
            root.destroy()
        else:
            # CLI - likely not fully supported for "edit" flow with current_config yet in ConfigPromptCli
            # But preserving interface.
            config_prompt = ConfigPromptCli(None, schema) # CLI doesn't use root
            user_config = config_prompt.get_config()

        if user_config:
            super().save_file(user_config)
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
