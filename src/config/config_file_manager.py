import os
import json
import sys
import tkinter as tk

from config.config_prompt_cli import ConfigPromptCli
from config.config_prompt_gui import ConfigPromptGui


class ConfigFileManager:
    ENCRYPTED_FIELDS = ['steam_api_key',
                        'steamgriddb_api_key',
                        'dropbox_app_key',
                        'dropbox_app_secret',
                        'dropbox_refresh_token',
                        ]

    def _get_config_path(self):
        if os.name == 'nt':  # Windows
            return os.path.join(os.getenv('APPDATA'), 'Steam Beautifier', 'config.json')
        else:  # Linux and other OS
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


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


    def _save_preferences(self, config):
        # Encrypt all fields that need to be encrypted
        config_out = config.copy()
        for field in self.ENCRYPTED_FIELDS:
            if field in config:
                config_out[field] = self._encrypt(config[field])

        config_out['_encrypted_fields'] = self.ENCRYPTED_FIELDS  # Store the list of encrypted fields
        config_path = self._get_config_path()
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config_out, f, indent=4)
        return config_path


    def _load_preferences(self):
        config_path = self._get_config_path()
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"Loaded config file: {config_path}")

            # Decrypt all encrypted fields
            for field in config.get('_encrypted_fields', []):
                if field in config:
                    config[field] = self._decrypt(config[field])

        else:
            config = None
        return config


    def load_or_create_preferences(self):
        config = self._load_preferences()
        if not config:
            config = self._prompt_user_for_config()
            self._save_preferences(config)
        return config


    def _encrypt(self, data):
        # TODO: Implement your encryption logic here
        return data  # Replace this with actual encryption


    def _decrypt(self, data):
        # TODO: Implement your decryption logic here
        return data  # Replace this with actual decryption
