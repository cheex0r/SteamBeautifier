from cloud.dropbox_manager import DropboxManager
from config.config_file_manager import ConfigFileManager
from config.start_on_boot_manager import StartOnBootManager
from steam.steam_directory_finder import get_grid_path_from_steamid64
from steam.steam_image_downloader import download_missing_images
from steam.launch_steam import launch_steam
from steam.steam_remove_whats_new import remove_whats_new


def main():
    config_file_manager = ConfigFileManager()
    preferences = config_file_manager.load_or_create_preferences()

    StartOnBootManager.start_on_boot(preferences.get('start_on_boot', False))
    steam_id64 = preferences['steam_id']
    local_grid_file_path = get_grid_path_from_steamid64(steam_id64)
    dropbox_file_path = [steam_id64, 'grid']
    
    if preferences['remove_whats_new']:
        remove_whats_new()
    if preferences['launch'] or preferences['bigpicture']:
        launch_steam(preferences['bigpicture'])
    if preferences['dropbox_app_key']:
        dropbox_manager = DropboxManager(config_file_manager)
        dropbox_manager.download_newer_files(local_grid_file_path, dropbox_file_path)
    if preferences['download-images']:
        download_missing_images(preferences['steam_api_key'], 
                                preferences['steamgriddb_api_key'], 
                                steam_id64)
    if preferences['dropbox_app_key']:
        dropbox_manager = DropboxManager(config_file_manager)
        dropbox_manager.upload_newer_files(local_grid_file_path, dropbox_file_path)


if __name__ == "__main__":
    main()

