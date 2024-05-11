import json

from steam_remove_whats_new import remove_whats_new
from launch_steam import launch_steam

def load_preferences():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_preferences(preferences):
    with open('config.json', 'w') as f:
        json.dump(preferences, f)

def prompt_for_preferences():
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
    save_preferences(preferences)
    return preferences

def main():
    preferences = load_preferences()
    if not preferences:
        preferences = prompt_for_preferences()
    print("Preferences:", preferences)

    if preferences['remove_whats_new']:
        remove_whats_new()
    if preferences['launch'] or preferences['bigpicture']:
        launch_steam(preferences['bigpicture'])

if __name__ == "__main__":
    main()