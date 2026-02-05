import os
import argparse
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from filemanagers.config_file_manager import ConfigFileManager
from api_proxies.nextcloud_api_proxy import NextcloudApiProxy
from cloud.nextcloud_manager import NextcloudManager
from steam.steam_image_handler import extract_appid_and_postfix
from steam.steam_directory_finder import get_grid_path
from steam.steam_id import SteamId

STEAM_GRID_SYNC_DIR = "SteamGridSync"
NON_STEAM_DIR = "SteamShortcutGridSync"

def cleanup_local_duplicates(local_dir, dry_run=False):
    print(f"\nScanning local folder: {local_dir}")
    if not os.path.exists(local_dir):
        print("Local folder does not exist.")
        return

    files = os.listdir(local_dir)
    # Group by appid+postfix
    groups = {}
    for f in files:
        if f.lower() == 'desktop.ini' or f.startswith('.'): continue
        try:
            appid, postfix, ext = extract_appid_and_postfix(f)
            key = (appid, postfix)
            if key not in groups: groups[key] = []
            groups[key].append(f)
        except ValueError:
            pass

    for key, duplicates in groups.items():
        if len(duplicates) > 1:
            print(f"Found duplicates for {key}: {duplicates}")
            # Sort by timestamp (newest first)
            # We check max(mtime, ctime)
            def get_sort_key(filename):
                path = os.path.join(local_dir, filename)
                return max(os.path.getmtime(path), os.path.getctime(path))
            
            duplicates.sort(key=get_sort_key, reverse=True)
            keep = duplicates[0]
            remove = duplicates[1:]
            
            print(f"  -> Keeping: {keep}")
            for r in remove:
                print(f"  -> Deleting: {r}")
                if not dry_run:
                    os.remove(os.path.join(local_dir, r))

def cleanup_remote_duplicates(manager, remote_folder, dry_run=False):
    print(f"\nScanning remote folder: {remote_folder}")
    files_map = manager.list_remote_files(remote_folder) # filename -> mtime
    
    groups = {}
    for filename, mtime in files_map.items():
        try:
            appid, postfix, ext = extract_appid_and_postfix(filename)
            key = (appid, postfix)
            if key not in groups: groups[key] = []
            groups[key].append((filename, mtime))
        except ValueError:
            pass

    for key, duplicates in groups.items():
        if len(duplicates) > 1:
            print(f"Found duplicates for {key}: {[d[0] for d in duplicates]}")
            # Sort by mtime (newest first)
            duplicates.sort(key=lambda x: x[1], reverse=True)
            keep = duplicates[0]
            remove = duplicates[1:]
            
            print(f"  -> Keeping: {keep[0]} (mtime: {keep[1]})")
            for r in remove:
                print(f"  -> Deleting: {r[0]} (mtime: {r[1]})")
                if not dry_run:
                    manager.delete_file(f"{remote_folder}/{r[0]}")

def main():
    parser = argparse.ArgumentParser(description="Cleanup duplicate images (conflicting extensions)")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without deleting")
    args = parser.parse_args()

    config_manager = ConfigFileManager()
    config = config_manager.load_or_create_preferences()

    if not config or not config.get('nextcloud_url'):
        print("Nextcloud not configured.")
        return

    print("Connecting to Nextcloud...")
    
    # We need to iterate over configured Steam IDs
    steam_ids = str(config.get('steam_id', '*')).split(',')
    
    # Resolving * is harder without importing steam logic, let's assume specific ID or just ask Config?
    # Actually main.py handles * logic. For this side tool, let's just use what's in config or warn.
    # If '*', relies on get_steam_ids().
    if '*' in steam_ids:
        from steam.steam_directory_finder import get_steam_ids
        steam_ids_obj = get_steam_ids()
        steam_ids = [s.get_steamid() for s in steam_ids_obj]

    for steam_id in steam_ids:
        steam_id = steam_id.strip()
        print(f"\nProcessing Steam ID: {steam_id}")
        
        # 1. Local path
        local_path = get_grid_path(SteamId(steamid64=steam_id))
        cleanup_local_duplicates(local_path, args.dry_run)
        
        # 2. Remote
        cloud_base = config.get('nextcloud_base_folder', 'SteamBeautifier')
        cloud_folder = f"{cloud_base}/{steam_id}"
        api_proxy = NextcloudApiProxy(config['nextcloud_url'], config['nextcloud_user'], config['nextcloud_password'])
        manager = NextcloudManager(api_proxy, cloud_folder)
        
        cleanup_remote_duplicates(manager, STEAM_GRID_SYNC_DIR, args.dry_run)
        cleanup_remote_duplicates(manager, NON_STEAM_DIR, args.dry_run)

if __name__ == "__main__":
    main()
