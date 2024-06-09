from steam_remove_whats_new import remove_whats_new
from launch_steam import launch_steam
from config.config_file_manager import ConfigFileManager


def main():
    config_file_manager = ConfigFileManager()
    preferences = config_file_manager.load_preferences_or_create()
    print("Preferences:", preferences)

    if preferences['remove_whats_new']:
        remove_whats_new()
    if preferences['launch'] or preferences['bigpicture']:
        launch_steam(preferences['bigpicture'])

if __name__ == "__main__":
    main()