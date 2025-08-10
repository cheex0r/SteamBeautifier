from api_proxies.nextcloud_api_proxy import NextcloudApiProxy
from cloud.nextcloud_manager import NextcloudManager
from cloud.steam_grid_sync_manager import SteamGridSyncManager


def execute(context, config):
    if not config.get('nextcloud_sync', False):
        return
    
    steam_id = context.get('steam_id')
    local_grid_file_path = context.get('local_grid_file_path')
    non_steam_games = context.get('non_steam_games', [])

    print(f"Nextcloud URL: {config['nextcloud_url']}")
    cloud_folder = f"{config.get('nextcloud_base_folder', 'SteamBeautifier')}/{steam_id.get_steamid()}"
    api_proxy = NextcloudApiProxy(config['nextcloud_url'], config['nextcloud_user'], config['nextcloud_password'])
    nextcloud_manager = NextcloudManager(api_proxy, cloud_folder)
    sync_manager = SteamGridSyncManager(nextcloud_manager, non_steam_games)

    if not sync_manager:
        return

    try:
        sync_manager.download_steam_games_grid(local_grid_file_path)
    except Exception as e:
        print(f"Error downloading Steam games grid: {e}")
    try:
        sync_manager.download_non_steam_games_grid(local_grid_file_path)
    except Exception as e:
        print(f"Error downloading non-Steam games: {e}")