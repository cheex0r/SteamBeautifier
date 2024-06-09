import os
import json
import tkinter as tk

from config.config_prompt_gui import ConfigPromptGui
from config.config_prompt_cli import ConfigPromptCli

class ConfigFileManager:
    def get_config_path(self):
        if os.name == 'nt':  # Windows
            return os.path.join(os.getenv('APPDATA'), 'Steam Beautifier', 'config.json')
        else:  # Linux and other OS
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        
    def get_config_schema(self):
        with open('config_schema.json', 'r') as schema_file:
            schema = json.load(schema_file)
        return schema

    def create_preferences(self, use_gui=True):
        schema = self.get_config_schema()
        if use_gui:
            root = tk.Tk()
            config_prompt = ConfigPromptGui(root, schema)
        else:
            config_prompt = ConfigPromptCli(root, schema)
        user_preferences = config_prompt.get_user_preferences()
        return user_preferences


    def save_preferences(self, preferences):
        config_path = self.get_config_path()
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(preferences, f, indent=4)

        return config_path

    def load_preferences(self):
        config_path = self.get_config_path()

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                preferences = json.load(f)
        else:
            preferences = None
        
        return preferences

    def load_preferences_or_create(self):
        preferences = self.load_preferences()
        if not preferences:
            preferences = self.create_preferences()
            self.save_preferences(preferences)
        return preferences