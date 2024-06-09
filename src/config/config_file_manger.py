import os
import json

def save_preferences(preferences):
    # Define the path to the config file
    config_dir = os.getenv('APPDATA', os.path.expanduser('~'))
    config_path = os.path.join(config_dir, 'Steam Beautifier', 'config.json')
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # Write preferences to the config file
    with open(config_path, 'w') as f:
        json.dump(preferences, f, indent=4)

    return config_path

def load_preferences():
    # Define the path to the config file
    config_dir = os.getenv('APPDATA', os.path.expanduser('~'))
    config_path = os.path.join(config_dir, 'Steam Beautifier', 'config.json')

    # If the config file exists, load preferences from it
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            preferences = json.load(f)
    else:
        # If the config file doesn't exist, return an empty dictionary
        preferences = {}
    
    return preferences
