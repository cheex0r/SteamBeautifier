from cloud.dropbox_manager import DropboxManager
from filemanagers.config_file_manager import ConfigFileManager
from config.start_on_boot_manager import start_on_boot
from steam.launch_steam import launch_steam
from steam.steam_directory_finder import get_grid_path, get_steam_ids
from steam.steam_image_downloader import download_missing_images
from steam.steam_remove_whats_new import remove_whats_new
from steam.steam_shortcuts_manager import parse_shortcuts_vdf
from steam.steam_id import SteamId
from steam.steam_directory_finder import get_steam_path
from filemanagers.dropbox_manifest_file_manager import DropboxManifestFileManager

from api_proxies.nextcloud_api_proxy import NextcloudApiProxy
from cloud.nextcloud_manager import NextcloudManager
from cloud.steam_grid_sync_manager import SteamGridSyncManager


def main():
    config_file_manager = ConfigFileManager()
    config = config_file_manager.load_or_create_preferences()

    start_on_boot(config.get('start_on_boot', False))
    if config['remove_whats_new']:
        remove_whats_new()
    if config['launch'] or config['bigpicture']:
        launch_steam(config['bigpicture'])
    steam_path = get_steam_path()
    steam_ids = _get_steam_ids(config)

    for steam_id in steam_ids: 
        _run_tasks_for_user(config, steam_path, steam_id)


def _run_tasks_for_user(config, steam_path, steam_id: SteamId):
    local_grid_file_path = get_grid_path(steam_id)
    non_steam_games = parse_shortcuts_vdf(steam_path, steam_id)
    sync_manager = None

    if config.get('nextcloud_url', False):
        print(f"Nextcloud URL: {config['nextcloud_url']}")
        cloud_folder = f"{config.get('nextcloud_base_folder', 'SteamBeautifier')}/{steam_id.get_steamid()}"
        api_proxy = NextcloudApiProxy(config['nextcloud_url'], config['nextcloud_user'], config['nextcloud_password'])
        nextcloud_manager = NextcloudManager(api_proxy, cloud_folder)
        sync_manager = SteamGridSyncManager(nextcloud_manager, non_steam_games)

    if sync_manager:
        try:
            sync_manager.download_steam_games_grid(local_grid_file_path)
        except Exception as e:
            print(f"Error downloading Steam games grid: {e}")
        try:
            sync_manager.download_non_steam_games_grid(local_grid_file_path)
        except Exception as e:
            print(f"Error downloading non-Steam games: {e}")
    
    dropbox_manager = None
    if config['dropbox_sync']:
        dropbox_manifest_file_manager = DropboxManifestFileManager(steam_id)
        dropbox_manifest = dropbox_manifest_file_manager.load_or_create_manifest()
        dropbox_manager = _get_dropbox_manager(config, steam_id, dropbox_manifest)

    if dropbox_manager:
        dropbox_manager.download_newer_files(
            local_grid_file_path,
            non_steam_games)

    if config['download-images']:
        download_missing_images(
            config['steam_api_key'],
            config['steamgriddb_api_key'],
            steam_id)

    if dropbox_manager:
        dropbox_manager.upload_newer_files(
            local_grid_file_path,
            non_steam_games)
        dropbox_manifest_file_manager.save_file(dropbox_manager.get_manifest())
        dropbox_manager.upload_manifest()
    
    if sync_manager:
        sync_manager.upload_directory(local_grid_file_path)


def _get_dropbox_manager(config, steam_id, dropbox_manifest):
    try:
        return DropboxManager(
            app_key=config['dropbox_app_key'],
            app_secret=config['dropbox_app_secret'],
            refresh_token=config['dropbox_refresh_token'],
            steam_id=steam_id,
            manifest=dropbox_manifest
        )
    except KeyError as e:
        print(f"Error reading Dropbox values even though 'dropbox_sync' is true: {e}. Please run the configuration setup.")
        return None


def _get_steam_ids(config):
    steam_ids = []
    steam_id64s = config.get('steam_id', '*')
    if steam_id64s.strip() == '*':
        steam_ids = get_steam_ids()
    else:
        steam_ids = [SteamId(steamid64=steam_id64.strip()) for steam_id64 in steam_id64s.split(',')]
    return steam_ids


if __name__ == "__main__":
    main()

