import concurrent.futures
import dropbox
import hashlib
import os
import requests
from tqdm import tqdm

from dropbox.files import WriteMode
from dropbox.exceptions import AuthError

from cloud.constants import DROPBOX_GRID_DIRECTORY, DROPBOX_GRID_DIRECTORY_NON_STEAM
from steam.steam_id import SteamId


class DropboxManager:
    def __init__(self, app_key, app_secret, refresh_token):
        self.app_key = app_key
        self.app_secret = app_secret
        self.refresh_token = refresh_token


    def download_newer_files(self, local_folder, steam_id: SteamId, non_steam_games={}):
        access_token = self._get_access_token()
        if not access_token:
            print("Dropbox access token not found. Please authenticate first.")
            return
        
        dropbox_folder_path = DROPBOX_GRID_DIRECTORY.format(user_id=steam_id.get_steamid())
        dropbox_folder_path_non_steam = DROPBOX_GRID_DIRECTORY_NON_STEAM.format(user_id=steam_id.get_steamid())

        if not os.path.exists(local_folder):
            os.makedirs(local_folder)

        # Rekey the non-Steam games dictionary to use the name as the key
        non_steam_games = {self._hash_game_name(game['AppName']): game for game in non_steam_games.values()}

        self._download_newer_files_for_category(access_token, local_folder, dropbox_folder_path, non_steam_games, is_steam=True)
        self._download_newer_files_for_category(access_token, local_folder, dropbox_folder_path_non_steam, non_steam_games, is_steam=False)


    def upload_newer_files(self, local_folder, steam_id: SteamId, non_steam_games={}):
        access_token = self._get_access_token()
        if not access_token:
            print("Dropbox access token not found. Please authenticate first.")
            return
        
        dbx_folder_path = DROPBOX_GRID_DIRECTORY.format(user_id=steam_id.get_steamid())
        dbx_folder_path_non_steam = DROPBOX_GRID_DIRECTORY_NON_STEAM.format(user_id=steam_id.get_steamid())

        steam_app_files = []
        non_steam_app_files = []

        files = os.listdir(local_folder)
        for file in files:
            game_id, postfix = self._extract_gameid_from_filename(file)
            if game_id in non_steam_games:
                non_steam_app_files.append(file)
            elif len(game_id) < 10: # Skip stale images to old shortcuts
                steam_app_files.append(file)

        self._upload_newer_files(access_token, local_folder, steam_app_files, dbx_folder_path)
        self._upload_newer_files(access_token, local_folder, non_steam_app_files, dbx_folder_path_non_steam, non_steam_games)


    def _get_access_token(self):
        url = "https://api.dropbox.com/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.app_key,
            "client_secret": self.app_secret,
        }

        response = requests.post(url, data=data)
        response_data = response.json()

        if response.status_code == 200:
            access_token = response_data['access_token']
            return access_token
        else:
            print(f"Failed to refresh access token: {response.content}")
            return None


    def _download_newer_files_for_category(self, access_token, local_folder, dropbox_folder_path, non_steam_games, is_steam):       
        dbx = dropbox.Dropbox(access_token)

        try:
            # Retrieve all file metadata in the Dropbox folder, handling pagination
            dropbox_file_metadata = self._get_all_file_hashes_in_dropbox_folder(dbx, dropbox_folder_path)
            def process_file(dropbox_file_name, dropbox_file_hash):
                game_name, postfix = self._extract_gameid_from_filename(dropbox_file_name)
                clean_game_name = game_name.strip('{}')
                local_file_name = dropbox_file_name

                if not is_steam:
                    if clean_game_name not in non_steam_games:
                        return  0
                    local_file_name = f"{non_steam_games[clean_game_name]['GridImageId']}{postfix}"

                local_file_path = os.path.join(local_folder, local_file_name)

                if os.path.isfile(local_file_path):
                    local_file_hash = self._calculate_dropbox_content_hash(local_file_path)
                    if local_file_hash != dropbox_file_hash:
                        tqdm.write(f"Downloading from Dropbox {dropbox_folder_path}/{dropbox_file_name} to {local_file_path}")
                        self._download_file_from_dropbox(access_token, dropbox_folder_path + '/' + dropbox_file_name, local_file_path)
                        return 1
                else:
                    tqdm.write(f"Downloading from Dropbox {dropbox_folder_path}/{dropbox_file_name} to {local_file_path}")
                    self._download_file_from_dropbox(access_token, dropbox_folder_path + '/' + dropbox_file_name, local_file_path)
                    return 1
                return 0

            with concurrent.futures.ThreadPoolExecutor() as executor:
                num_downloads = sum(tqdm(executor.map(lambda item: process_file(item[0], item[1]), dropbox_file_metadata.items()), total=len(dropbox_file_metadata), desc="Downloading files from Dropbox"))
            print(f"Downloaded {num_downloads} files from Dropbox")

        except dropbox.exceptions.ApiError as e:
            print(f"Error during the download and verification process: {e}")


    def _download_file_from_dropbox(self, access_token, dropbox_path, local_path):
        dbx = dropbox.Dropbox(access_token)
        try:
            metadata, res = dbx.files_download(path=dropbox_path)
            with open(local_path, 'wb') as f:
                f.write(res.content)
        except dropbox.exceptions.ApiError as e:
            print(f"Error downloading file: {e}")


    def _upload_newer_files(self, access_token, local_folder, files, dbx_folder, non_steam_games={}):
        dbx = dropbox.Dropbox(access_token)
        total_files = len(files)

        try:
            # Retrieve all file hashes in the Dropbox folder, handling pagination
            dropbox_file_hashes = self._get_all_file_hashes_in_dropbox_folder(dbx, dbx_folder)

            def process_file(local_file_name):
                game_id, postfix = self._extract_gameid_from_filename(local_file_name)
                local_file_path = os.path.join(local_folder, local_file_name)
                dbx_filename = local_file_name
                if game_id in non_steam_games:
                    hash_game_name = self._hash_game_name(non_steam_games[game_id]['AppName'])
                    dbx_filename = f"{hash_game_name}{postfix}"
                
                if os.path.isfile(local_file_path):
                    local_file_hash = self._calculate_dropbox_content_hash(local_file_path)
                    if dbx_filename in dropbox_file_hashes:
                        dropbox_file_hash = dropbox_file_hashes[dbx_filename]
                        if local_file_hash != dropbox_file_hash:
                            tqdm.write(f"Uploading {local_file_path} to Dropbox {dbx_folder}/{dbx_filename}")
                            self._upload_file_to_dropbox(access_token, local_file_path, dbx_folder, dbx_filename)
                            return 1
                    else:
                        tqdm.write(f"Uploading {local_file_path} to Dropbox {dbx_folder}/{dbx_filename}")
                        self._upload_file_to_dropbox(access_token, local_file_path, dbx_folder, dbx_filename)
                        return 1
                return 0
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                num_uploaded = sum(tqdm(executor.map(process_file, files), total=total_files, desc="Uploading files to Dropbox"))
            print(f"Uploaded {num_uploaded} files to Dropbox")


        except dropbox.exceptions.ApiError as e:
            print(f"Error during the upload and verification process: {e}")



    def _upload_file_to_dropbox(self, access_token, local_file_path, dropbox_folder, new_filename=None):
        dbx = dropbox.Dropbox(access_token)
        if new_filename is None:
            new_filename = os.path.basename(local_file_path)
        dropbox_file_path = f"{dropbox_folder}/{new_filename}"
        
        with open(local_file_path, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_file_path, mode=dropbox.files.WriteMode('overwrite'))


    def _calculate_dropbox_content_hash(self, file_path):
        """
        Calculate the Dropbox content hash for a given file.
        Dropbox content hash is calculated by splitting the file into 4MB chunks,
        SHA-256 hashing each chunk, concatenating the results, and then hashing
        the concatenated result again.
        """
        block_size = 4 * 1024 * 1024  # 4MB
        hash_func = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(block_size)
                if not chunk:
                    break
                chunk_hash = hashlib.sha256(chunk).digest()
                hash_func.update(chunk_hash)
        return hash_func.hexdigest()
    

    def _get_all_file_hashes_in_dropbox_folder(self, dbx, folder_path):
        file_hashes = {}
        try:
            result = dbx.files_list_folder(folder_path)
            file_hashes.update({entry.name: entry.content_hash for entry in result.entries if isinstance(entry, dropbox.files.FileMetadata)})

            while result.has_more:
                result = dbx.files_list_folder_continue(result.cursor)
                file_hashes.update({entry.name: entry.content_hash for entry in result.entries if isinstance(entry, dropbox.files.FileMetadata)})

        except dropbox.exceptions.ApiError as e:
            print(f"Error listing files in Dropbox folder: {e}")

        return file_hashes
    

    def _hash_game_name(self, game_name):
        return hashlib.sha256(game_name.encode('utf-8')).hexdigest()


    def _generate_hashed_filename(self, game_name, postfix):
        hashed_name = self._hash_game_name(game_name)
        separator = "-"
        return f"{hashed_name}{separator}{postfix}"


    def _extract_gameid_from_filename(self, filepath):
        filename_with_extension = os.path.basename(filepath)
        filename, extension = os.path.splitext(filename_with_extension)
        
        if '-' in filename:
            hashed_part, postfix = filename.split('-', 1)
            return hashed_part, f"-{postfix}{extension}"
        else:
            filename = filename.split('_')[0]
            filename = filename.rstrip('p')
            postfix = filename_with_extension[len(filename):]
            return filename, postfix
