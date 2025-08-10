from config.start_on_boot_manager import start_on_boot
from filemanagers.config_file_manager import ConfigFileManager
from steam.steam_directory_finder import get_grid_path, get_steam_ids
from steam.steam_shortcuts_manager import parse_shortcuts_vdf
from steam.steam_id import SteamId
from steam.steam_directory_finder import get_steam_path
from tasks import (
    task_cloud_sync_download,
    task_cloud_sync_upload,
    task_download_missing_imgs,
    task_remove_whats_new,
    task_start_steam
)

def main():
    config_file_manager = ConfigFileManager()
    config = config_file_manager.load_or_create_preferences()

    start_on_boot(config.get('start_on_boot', False))
        
    steam_path = get_steam_path()
    steam_ids = _get_steam_ids(config)

    task_remove_whats_new.execute(None, config)
    task_start_steam.execute(None, config)

    for steam_id in steam_ids: 
        _run_tasks_for_user(config, steam_path, steam_id)


def _run_tasks_for_user(config, steam_path, steam_id: SteamId):
    context = {
        'steam_id': steam_id,
        'local_grid_file_path': get_grid_path(steam_id),
        'non_steam_games': parse_shortcuts_vdf(steam_path, steam_id)
    }
    tasks = [
        task_cloud_sync_download,
        task_download_missing_imgs,
        task_cloud_sync_upload,
    ]

    for task in tasks:
        task.execute(context, config)


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

