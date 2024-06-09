import os
import json

def get_config_path():
    if os.name == 'nt':  # Windows
        return os.path.join(os.getenv('APPDATA'), 'steam_beautifier', 'config.json')
    else:  # Linux and other OS
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return None

def save_config(config):
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def prompt_user_for_config():
    preferences = {}
    preferences['remove_whats_new'] = input("Remove What's New shelf? (True/False): ").lower() == 'true'
    preferences['launch'] = input("Launch Steam? (True/False): ").lower() == 'true'
    if preferences['launch']:
        preferences['bigpicture'] = input("Start Steam in Big Picture mode? (True/False): ").lower() == 'true'
    else:
        preferences['bigpicture'] = False
    preferences['download-images'] = input("Download missing grid art? (True/False): ").lower() == 'true'
    if preferences['download-images']:
        preferences['steam_api_key'] = input("Enter your Steam API Key: ")
        preferences['steamgriddb_api_key'] = input("Enter your SteamGridDB API Key: ")
        preferences['steam_id'] = int(input("Enter your SteamID64: "))
    return preferences

def main():
    config = load_config()
    if config is None:
        print("Configuration file not found. Please configure the application.")
        config = prompt_user_for_config()
        save_config(config)
    else:
        print("Configuration loaded successfully.")

if __name__ == '__main__':
    main()
