import concurrent.futures
import dropbox
import hashlib
import os
import requests
from datetime import datetime, timedelta, timezone
from tqdm import tqdm

from dropbox.files import WriteMode
from dropbox.exceptions import AuthError


class DropboxManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager


    def _get_dropbox_access_token(self):
        preferences = self.config_manager._load_preferences()
        access_token = preferences.get('dropbox_access_token')
        refresh_token = preferences.get('dropbox_refresh_token')
        token_expiry = preferences.get('dropbox_token_expiry')

        if access_token and token_expiry:
            token_expiry = datetime.strptime(token_expiry, '%Y-%m-%d %H:%M:%S')
            if datetime.now() >= token_expiry:
                access_token = self._refresh_dropbox_access_token(refresh_token)
        
        return access_token
    

    def _refresh_dropbox_access_token(self, refresh_token):
        preferences = self.config_manager._load_preferences()
        refresh_token = preferences.get('dropbox_refresh_token')
        app_key = preferences.get('dropbox_app_key')
        app_secret = preferences.get('dropbox_app_secret')
        
        url = "https://api.dropbox.com/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": app_key,
            "client_secret": app_secret,
        }

        response = requests.post(url, data=data)
        response_data = response.json()

        if response.status_code == 200:
            new_access_token = response_data['access_token']
            expires_in = response_data.get('expires_in', 14400)  # 14400 seconds = 4 hours
            self._save_dropbox_access_token(new_access_token, refresh_token, expires_in)
            return new_access_token
        else:
            print(f"Failed to refresh access token: {response.content}")
            return None


    # TODO: Encrypt sensitive data before saving to disk
    def _save_dropbox_access_token(self, access_token, refresh_token, expires_in=14400):
        preferences = self.config_manager._load_preferences() or {}
        preferences['dropbox_access_token'] = access_token
        preferences['dropbox_refresh_token'] = refresh_token
        preferences['dropbox_token_expiry'] = (datetime.now() + timedelta(seconds=expires_in)).strftime('%Y-%m-%d %H:%M:%S')
        self.config_manager._save_preferences(preferences)


    def _save_dropbox_app_details(self, app_key, app_secret):
        preferences = self.config_manager._load_preferences() or {}
        preferences['dropbox_app_key'] = app_key
        preferences['dropbox_app_secret'] = app_secret
        self.config_manager._save_preferences(preferences)


    def _upload_file_to_dropbox(self, access_token, local_file_path, dropbox_folder):
        dbx = dropbox.Dropbox(access_token)
        with open(local_file_path, 'rb') as f:
            dropbox_file_path = f"{dropbox_folder}/{os.path.basename(local_file_path)}"
            dbx.files_upload(f.read(), dropbox_file_path, mode=WriteMode('overwrite'))


    def _download_file_from_dropbox(self, access_token, dropbox_path, local_path):
        dbx = dropbox.Dropbox(access_token)
        try:
            metadata, res = dbx.files_download(path=dropbox_path)
            with open(local_path, 'wb') as f:
                f.write(res.content)
        except dropbox.exceptions.ApiError as e:
            print(f"Error downloading file: {e}")


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


    def authenticate_dropbox(self, app_key, app_secret):
        self._save_dropbox_app_details(app_key, app_secret)
        auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(app_key, app_secret, token_access_type='offline')
        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print("2. Click 'Allow' (you might have to log in first)")
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()
        
        try:
            oauth_result = auth_flow.finish(auth_code)
            print(oauth_result)
            self._save_dropbox_access_token(oauth_result.access_token, oauth_result.refresh_token)
        except AuthError as e:
            print(f"Error during authentication: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e.response.status_code} {e.response.reason}")
            print(f"Response content: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def download_newer_files(self, local_folder, dropbox_folder_list):
        dropbox_folder_path = '/' + '/'.join(dropbox_folder_list)
        access_token = self._get_dropbox_access_token()
        if not access_token:
            print("Dropbox access token not found. Please authenticate first.")
            return

        dbx = dropbox.Dropbox(access_token)

        # Ensure the local folder exists
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)

        try:
            # Retrieve all file hashes in the Dropbox folder, handling pagination
            dropbox_file_metadata = self._get_all_file_hashes_in_dropbox_folder(dbx, dropbox_folder_path)

            def process_file(local_file_name):
                local_file_path = os.path.join(local_folder, local_file_name)
                if os.path.isfile(local_file_path):
                    local_file_hash = self._calculate_dropbox_content_hash(local_file_path)
                    
                    if local_file_name in dropbox_file_metadata:
                        dropbox_file_hash = dropbox_file_metadata[local_file_name]

                        if local_file_hash != dropbox_file_hash:
                            self._download_file_from_dropbox(access_token, dropbox_folder_path + '/' + local_file_name, local_file_path)
                    else:
                        self._download_file_from_dropbox(access_token, dropbox_folder_path + '/' + local_file_name, local_file_path)
                else:
                    self._download_file_from_dropbox(access_token, dropbox_folder_path + '/' + local_file_name, local_file_path)

            # Use ThreadPoolExecutor to parallelize the downloading process
            with concurrent.futures.ThreadPoolExecutor() as executor:
                list(tqdm(executor.map(process_file, os.listdir(local_folder)), total=len(os.listdir(local_folder)), desc="Downloading files from Dropbox"))

        except dropbox.exceptions.ApiError as e:
            print(f"Error during the download and verification process: {e}")


    def upload_newer_files(self, local_folder, dropbox_folder_list):
        dropbox_folder_path = '/' + '/'.join(dropbox_folder_list)
        access_token = self._get_dropbox_access_token()
        if not access_token:
            print("Dropbox access token not found. Please authenticate first.")
            return

        dbx = dropbox.Dropbox(access_token)

        try:
            # Retrieve all file hashes in the Dropbox folder, handling pagination
            dropbox_file_hashes = self._get_all_file_hashes_in_dropbox_folder(dbx, dropbox_folder_path)

            def process_file(local_file_name):
                local_file_path = os.path.join(local_folder, local_file_name)
                if os.path.isfile(local_file_path):
                    local_file_hash = self._calculate_dropbox_content_hash(local_file_path)
                    if local_file_name in dropbox_file_hashes:
                        dropbox_file_hash = dropbox_file_hashes[local_file_name]
                        if local_file_hash != dropbox_file_hash:
                            self._upload_file_to_dropbox(access_token, local_file_path, dropbox_folder_path)
                    else:
                        self._upload_file_to_dropbox(access_token, local_file_path, dropbox_folder_path)

            # Use ThreadPoolExecutor to parallelize the processing
            with concurrent.futures.ThreadPoolExecutor() as executor:
                list(tqdm(executor.map(process_file, os.listdir(local_folder)), total=len(os.listdir(local_folder)), desc="Uploading files to Dropbox"))

        except dropbox.exceptions.ApiError as e:
            print(f"Error during the upload and verification process: {e}")

