import os
import concurrent.futures

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


    def upload_directory(self, local_dir, progress=None, task_id=None):
        """
        Process all files in a local directory for upload.
        If the local directory does not exist, the function will exit gracefully.
        
        Args:
            local_dir (str): The path to the local directory containing files to upload.
        """
        if not os.path.isdir(local_dir):
            print(f"Info: Local source directory not found: '{local_dir}'. Skipping sync for this folder.")
            return # Exit the function gracefully

        self.cloud_manager.ensure_remote_folder(STEAM_GRID_SYNC_DIR)
        self.cloud_manager.ensure_remote_folder(NON_STEAM_DIR)

        # Pre-fetch remote file lists to avoid N*PROPFIND requests
        steam_remote_files = self.cloud_manager.list_remote_files(STEAM_GRID_SYNC_DIR)
        non_steam_remote_files = self.cloud_manager.list_remote_files(NON_STEAM_DIR)

        files_to_process = [f for f in os.listdir(local_dir) if not (f.endswith('.log') or f.startswith('.') or f.lower() == 'desktop.ini')]
        
        if progress and task_id and len(files_to_process) > 0:
            current_total = 0
            for task in progress.tasks:
                if task.id == task_id:
                    current_total = task.total or 0
                    break
            progress.update(task_id, total=current_total + len(files_to_process))

        def process_upload(filename):
            local_file = os.path.join(local_dir, filename)
            if not os.path.isfile(local_file):
                return
            appid, postfix, extension = extract_appid_and_postfix(filename)
            
            cloud_filename = f"{STEAM_GRID_SYNC_DIR}/{filename}"
            remote_mod_time = steam_remote_files.get(filename)

            if self.non_steam_games.get(appid) is not None:
                new_filename = f"{self.non_steam_games[appid]['CloudName']}{postfix}{extension}"
                cloud_filename = f"{NON_STEAM_DIR}/{new_filename}"
                remote_mod_time = non_steam_remote_files.get(new_filename)

            self.cloud_manager.upload_file(local_file, cloud_filename, remote_mod_time=remote_mod_time)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_upload, f) for f in files_to_process]
            for future in concurrent.futures.as_completed(futures):
                if progress and task_id:
                    progress.update(task_id, advance=1)


    def download_steam_games_grid(self, local_dir, progress=None, task_id=None):
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
        remote_files_list = list(remote_files.items())

        if progress and task_id and len(remote_files_list) > 0:
            current_total = 0
            for task in progress.tasks:
                if task.id == task_id:
                    current_total = task.total or 0
                    break
            progress.update(task_id, total=current_total + len(remote_files_list))

        def process_download_steam(item):
            filename, remote_mod_time = item
            local_file = os.path.join(local_dir, filename)
            cloud_filename = f"{STEAM_GRID_SYNC_DIR}/{filename}"

            # Conflict Resolution: Check for alternative extensions locally
            # 1. Parse current remote filename
            try:
                appid, postfix, extension = extract_appid_and_postfix(filename)
                
                # 2. Look for any local file matching `appid` + `postfix` + .*
                # e.g. if remote is 123.jpg, look for 123.png, 123.jpeg, etc.
                possible_conflicts = []
                for f in os.listdir(local_dir):
                    if f == filename: continue # Same file is handled by standard sync logic
                    
                    # Optimization: Filter by startswith first
                    if f.startswith(appid):
                         try:
                            l_appid, l_postfix, l_ext = extract_appid_and_postfix(f)
                            if l_appid == appid and l_postfix == postfix:
                                possible_conflicts.append(f)
                         except ValueError:
                             continue

                # 3. Compare with conflicts
                for conflict_file in possible_conflicts:
                    conflict_path = os.path.join(local_dir, conflict_file)
                    l_mtime = os.path.getmtime(conflict_path)
                    l_ctime = os.path.getctime(conflict_path)
                    
                    # Logic: If Local Alternative is NEWER -> Delete Remote File, Skip Download
                    if l_mtime > remote_mod_time or l_ctime > remote_mod_time:
                        return 
                    
                    # Logic: If Local Alternative is OLDER -> Delete Local File (allow download to replace it)
                    else:
                        os.remove(conflict_path)

            except ValueError:
                pass # Filename parse error, proceed normally

            self.cloud_manager.download_file(cloud_filename, local_file)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_download_steam, item) for item in remote_files_list]
            for future in concurrent.futures.as_completed(futures):
                if progress and task_id:
                    progress.update(task_id, advance=1)


    def download_non_steam_games_grid(self, local_dir, progress=None, task_id=None):
        """
        Download remote files for non-Steam games (shortcuts) that match the local non_steam_games list.
        
        Args:
            local_dir (str): Local directory where the files should be saved.
            remote_files (dict): Dictionary mapping remote filenames to their modification times.
        """
        remote_files = self.cloud_manager.list_remote_files(f"{NON_STEAM_DIR}")

        items_to_process = list(self.non_steam_games.items())
        if progress and task_id and len(items_to_process) > 0:
            current_total = 0
            for task in progress.tasks:
                if task.id == task_id:
                    current_total = task.total or 0
                    break
            progress.update(task_id, total=current_total + len(items_to_process))

        def process_download_non_steam(item):
            local_id, game_info = item
            cloud_name = game_info.get('CloudName')
            if not cloud_name:
                return

            for filename, remote_mod_time in remote_files.items():
                if cloud_name not in filename:
                    continue

                appid, postfix, extension = extract_appid_and_postfix(filename)
                
                local_filename = game_info.get('GridImageId', None)
                if local_filename is None:
                    continue
                local_filename = f"{local_id}{postfix}{extension}"
                local_file = os.path.join(local_dir, local_filename)

                remote_file_path = f"{NON_STEAM_DIR}/{filename}"
                self.cloud_manager.download_file(remote_file_path, local_file)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_download_non_steam, item) for item in items_to_process]
            for future in concurrent.futures.as_completed(futures):
                if progress and task_id:
                    progress.update(task_id, advance=1)
