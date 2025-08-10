from cloud.dropbox_manager import DropboxManager
from filemanagers.dropbox_manifest_file_manager import DropboxManifestFileManager


def execute(context, config):
    if not config.get('dropbox_sync', False):
        return
    
    steam_id = context.get('steam_id')
    local_grid_file_path = context.get('local_grid_file_path')
    non_steam_games = context.get('non_steam_games')

    dropbox_manifest_file_manager = DropboxManifestFileManager(steam_id)
    dropbox_manifest = dropbox_manifest_file_manager.load_or_create_manifest()
    dropbox_manager = _get_dropbox_manager(config, steam_id, dropbox_manifest)

    if not dropbox_manager:
        return

    dropbox_manager.download_newer_files(
        local_grid_file_path,
        non_steam_games)


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