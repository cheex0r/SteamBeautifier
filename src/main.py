from cloud.dropbox_manager import DropboxManager
from config.config_file_manager import ConfigFileManager
from config.start_on_boot_manager import start_on_boot
from steam.steam_directory_finder import get_grid_path
from steam.steam_image_downloader import download_missing_images
from steam.launch_steam import launch_steam
from steam.steam_remove_whats_new import remove_whats_new
from steam.steam_shortcuts_manager import parse_shortcuts_vdf
from steam.steam_id import SteamId
from steam.steam_directory_finder import get_steam_path


def main():
    config_file_manager = ConfigFileManager()
    preferences = config_file_manager.load_or_create_preferences()

    steam_id64 = preferences['steam_id']
    steam_id = SteamId(steamid64=steam_id64)

    local_grid_file_path = get_grid_path(steam_id)
    steam_path = get_steam_path()
    non_steam_games = parse_shortcuts_vdf(steam_path, steam_id)
    
    start_on_boot(preferences.get('start_on_boot', False))
    if preferences['remove_whats_new']:
        remove_whats_new()

    if preferences['launch'] or preferences['bigpicture']:
        launch_steam(preferences['bigpicture'])

    if preferences['dropbox_app_key']:
        dropbox_manager = DropboxManager(config_file_manager)
        dropbox_manager.download_newer_files(local_grid_file_path,
                                             steam_id,
                                             non_steam_games)

    if preferences['download-images']:
        download_missing_images(preferences['steam_api_key'],
                                preferences['steamgriddb_api_key'],
                                steam_id)

    if preferences['dropbox_app_key']:
        dropbox_manager = DropboxManager(config_file_manager)
        dropbox_manager.upload_newer_files(local_grid_file_path,
                                           steam_id,
                                           non_steam_games)


if __name__ == "__main__":
    main()

