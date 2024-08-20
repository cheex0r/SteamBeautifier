from config.config_file_manager import ConfigFileManager
from config.start_on_boot_manager import StartOnBootManager
from steam.steam_image_downloader import download_missing_images
from steam.launch_steam import launch_steam
from steam.steam_remove_whats_new import remove_whats_new


def main():
    config_file_manager = ConfigFileManager()
    preferences = config_file_manager.load_or_create_preferences()
    print("Preferences:", preferences)


    StartOnBootManager.start_on_boot(preferences['start_on_boot'])
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