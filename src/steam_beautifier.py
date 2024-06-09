from steam_remove_whats_new import remove_whats_new
from launch_steam import launch_steam
from config.config_file_manager import ConfigFileManager
from steam_image_downloader import download_missing_images


def main():
    config_file_manager = ConfigFileManager()
    preferences = config_file_manager.load_or_create_preferences()
    print("Preferences:", preferences)

    if preferences['remove_whats_new']:
        remove_whats_new()
    if preferences['launch'] or preferences['bigpicture']:
        launch_steam(preferences['bigpicture'])
    if preferences['download-images']:
        download_missing_images(preferences['steam_api_key'], 
                                preferences['steamgriddb_api_key'], 
                                preferences['steam_id'])


if __name__ == "__main__":
    main()