import dropbox
import os
import requests
from datetime import datetime

from config.config_file_manager import ConfigFileManager
from dropbox.files import WriteMode
from dropbox.exceptions import AuthError


class DropboxManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager


    def _get_dropbox_access_token(self):
        preferences = self.config_manager._load_preferences()
        return preferences.get('dropbox_access_token')


    def _save_dropbox_access_token(self, access_token):
        preferences = self.config_manager._load_preferences() or {}
        preferences['dropbox_access_token'] = access_token
        self.config_manager._save_preferences(preferences)


    def authenticate_dropbox(self, app_key, app_secret):
        auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print("2. Click 'Allow' (you might have to log in first)")
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()
        
        try:
            oauth_result = auth_flow.finish(auth_code)
            print(oauth_result)
            self._save_dropbox_access_token(oauth_result.access_token)
        except AuthError as e:
            print(f"Error during authentication: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e.response.status_code} {e.response.reason}")
            print(f"Response content: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def upload_image_to_dropbox(self, image_path):
        access_token = self._get_dropbox_access_token()
        if not access_token:
            print("Dropbox access token not found. Please authenticate first.")
            return

        dbx = dropbox.Dropbox(access_token)
        with open(image_path, 'rb') as f:
            dbx.files_upload(f.read(), '/' + os.path.basename(image_path), mode=WriteMode('overwrite'))
        print(f"Successfully uploaded {os.path.basename(image_path)} to Dropbox")


    def download_file_from_dropbox(self, access_token, dropbox_path, local_path):
        dbx = dropbox.Dropbox(access_token)
        try:
            metadata, res = dbx.files_download(path=dropbox_path)
            with open(local_path, 'wb') as f:
                f.write(res.content)
            print(f"Successfully downloaded {dropbox_path} to {local_path}")
        except dropbox.exceptions.ApiError as e:
            print(f"Error downloading file: {e}")


    def download_newer_files(self, dropbox_folder, local_folder):
        access_token = self._get_dropbox_access_token()
        if not access_token:
            print("Dropbox access token not found. Please authenticate first.")
            return

        dbx = dropbox.Dropbox(access_token)

        # Ensure the local folder exists
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)

        try:
            # List files in the Dropbox folder
            result = dbx.files_list_folder(dropbox_folder)
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    dropbox_file_path = entry.path_lower
                    local_file_path = os.path.join(local_folder, os.path.basename(dropbox_file_path))
                    
                    # Check if the local file exists and compare modification dates
                    if os.path.exists(local_file_path):
                        local_mod_time = datetime.fromtimestamp(os.path.getmtime(local_file_path))
                        dropbox_mod_time = entry.client_modified
                        if dropbox_mod_time > local_mod_time:
                            self.download_file_from_dropbox(access_token, dropbox_file_path, local_file_path)
                    else:
                        self.download_file_from_dropbox(access_token, dropbox_file_path, local_file_path)
        except dropbox.exceptions.ApiError as e:
            print(f"Error listing files in Dropbox folder: {e}")
