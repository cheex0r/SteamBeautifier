from cloud.dropbox_manager import DropboxManager
from config.config_file_manager import ConfigFileManager
from config.start_on_boot_manager import start_on_boot
from steam.launch_steam import launch_steam
from steam.steam_directory_finder import get_grid_path
from steam.steam_image_downloader import download_missing_images
from steam.steam_remove_whats_new import remove_whats_new
from steam.steam_shortcuts_manager import parse_shortcuts_vdf
from steam.steam_id import SteamId
from steam.steam_directory_finder import get_steam_path


def main():
    config_file_manager = ConfigFileManager()
    config = config_file_manager.load_or_create_preferences()

    steam_id64 = config['steam_id']
    steam_id = SteamId(steamid64=steam_id64)

    local_grid_file_path = get_grid_path(steam_id)
    steam_path = get_steam_path()
    non_steam_games = parse_shortcuts_vdf(steam_path, steam_id)
    
    start_on_boot(config.get('start_on_boot', False))
    if config['remove_whats_new']:
        remove_whats_new()

    if config['launch'] or config['bigpicture']:
        launch_steam(config['bigpicture'])

    dropbox_manager = None
    if config['dropbox_sync']:
        dropbox_manager = _get_dropbox_manager(config_file_manager)

    if dropbox_manager:
        dropbox_manager = _get_dropbox_manager(config_file_manager)
        dropbox_manager.download_newer_files(local_grid_file_path,
                                             steam_id,
                                             non_steam_games)

    if config['download-images']:
        download_missing_images(config['steam_api_key'],
                                config['steamgriddb_api_key'],
                                steam_id)

    if dropbox_manager:
        dropbox_manager = _get_dropbox_manager(config_file_manager)
        dropbox_manager.upload_newer_files(local_grid_file_path,
                                           steam_id,
                                           non_steam_games)
        

def _get_dropbox_manager(config_file_manager):
    try:
        return DropboxManager(
            app_key=config_file_manager.preferences['dropbox_app_key'],
            app_secret=config_file_manager.preferences['dropbox_app_secret'],
            refresh_token=config_file_manager.preferences['dropbox_refresh_token'],
        )
    except KeyError as e:
        print(f"Error: {e}. Please run the configuration setup.")
        return None


if __name__ == "__main__":
    main()

