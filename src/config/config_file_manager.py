import os
import json
import sys
import tkinter as tk

from config.config_prompt_cli import ConfigPromptCli
from config.config_prompt_gui import ConfigPromptGui

class ConfigFileManager:
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


    def _create_preferences(self, use_gui=True):
        schema = self._get_config_schema()
        if use_gui:
            root = tk.Tk()
            config_prompt = ConfigPromptGui(root, schema)
            root.mainloop()
            root.destroy()
        else:
            config_prompt = ConfigPromptCli(root, schema)
        user_preferences = config_prompt.get_user_preferences()
        return user_preferences


    def _save_preferences(self, preferences):
        config_path = self._get_config_path()
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(preferences, f, indent=4)

        return config_path

    def _load_preferences(self):
        config_path = self._get_config_path()

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                preferences = json.load(f)
            print(f"Loaded config file: {config_path}")
        else:
            preferences = None
        
        return preferences

    def load_or_create_preferences(self):
        preferences = self._load_preferences()
        if not preferences:
            preferences = self._create_preferences()
            self._save_preferences(preferences)
        return preferences