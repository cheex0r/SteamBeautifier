import os

from steam.steam_image_handler import extract_appid_and_postfix

STEAM_GRID_SYNC_DIR = "SteamGridSync"
NON_STEAM_DIR = "SteamShortcutGridSync"

class SteamGridSyncManager:
    def __init__(self, cloud_manager, non_steam_games):
        """
        Args:
            nc_api_proxy (NextcloudApiProxy): Instance to perform Nextcloud operations.
            non_steam_converter (object): An object or function that handles file name conversion.
        """
        self.cloud_manager = cloud_manager
        self.non_steam_games = non_steam_games
        self.reverse_non_steam_games = {value['CloudName']: key for key, value in non_steam_games.items() if 'CloudName' in value}


    def upload_directory(self, local_dir):
        """
        Process all files in a local directory for upload.
        
        Args:
            local_dir (str): The path to the local directory containing files to upload.
        """
        self.cloud_manager.ensure_remote_folder(STEAM_GRID_SYNC_DIR)
        self.cloud_manager.ensure_remote_folder(NON_STEAM_DIR)

        for filename in os.listdir(local_dir):
            if filename.endswith('.log') or filename.startswith('.') or filename.lower() == 'desktop.ini':
                continue

            print(f"Processing file: {filename}")
            local_file = os.path.join(local_dir, filename)
            if not os.path.isfile(local_file):
                continue  # Skip non-files
            appid, postfix, extension = extract_appid_and_postfix(filename)
            
            cloud_filename = f"{STEAM_GRID_SYNC_DIR}/{filename}"
            if self.non_steam_games.get(appid) is not None:
                # Convert the filename for non-Steam games.
                print(f"Found non-Steam game '{appid}' in the list.")
                cloud_filename = f"{NON_STEAM_DIR}/{self.non_steam_games[appid]['CloudName']}{postfix}{extension}"

            self.cloud_manager.upload_file(local_file, cloud_filename)


    def download_steam_games_grid(self, local_dir):
        """
        Process all remote files in the Nextcloud folder for download.
        Assumes that self.api_proxy.list_remote_files() returns a dictionary
        mapping remote filenames to their modification times.
        
        Args:
            local_dir (str): The path to the local directory where files will be downloaded.
        """
        # Retrieve remote files as a dictionary: {filename: mod_time}
        remote_files = self.cloud_manager.list_remote_files(f"{STEAM_GRID_SYNC_DIR}")

        # Process a subset if desired (here, we limit to the first 30 files)
        for filename, remote_mod_time in list(remote_files.items()):
            print(f"Processing remote file: {filename}")

            local_file = os.path.join(local_dir, filename)

            cloud_filename = f"{STEAM_GRID_SYNC_DIR}/{filename}"
            print(f"Downloading '{cloud_filename}' to '{local_file}'...")
            self.cloud_manager.download_file(cloud_filename, local_file)


    def download_non_steam_games_grid(self, local_dir):
        """
        Download remote files for non-Steam games (shortcuts) that match the local non_steam_games list.
        
        Args:
            local_dir (str): Local directory where the files should be saved.
            remote_files (dict): Dictionary mapping remote filenames to their modification times.
        """
        remote_files = self.cloud_manager.list_remote_files(f"{NON_STEAM_DIR}")

        for local_id, game_info in self.non_steam_games.items():
            cloud_name = game_info.get('CloudName')
            if not cloud_name:
                continue  # Skip if no CloudName is defined.
            
            # Look for a remote file that includes the CloudName.
            for filename, remote_mod_time in remote_files.items():
                if cloud_name not in filename:
                    continue

                print(f"Found remote file '{filename}' for non-Steam game '{local_id}'.")

                appid, postfix, extension = extract_appid_and_postfix(filename)
                
                # Determine the local filename.
                local_filename = game_info.get('GridImageId', None)
                if local_filename is None:
                    continue
                local_filename = f"{local_id}{postfix}{extension}"
                local_file = os.path.join(local_dir, local_filename)

                print(f"Downloading non-Steam game file '{filename}' to '{local_file}'...")
                # Use NON_STEAM_DIR instead of STEAM_GRID_SYNC_DIR for the remote file path.
                remote_file_path = f"{NON_STEAM_DIR}/{filename}"
                self.cloud_manager.download_file(remote_file_path, local_file)
