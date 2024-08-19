import dropbox
import os
import requests
from datetime import datetime, timedelta, timezone

from config.config_file_manager import ConfigFileManager
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
        url = "https://api.dropbox.com/oauth2/token"
        app_key = self.config_manager.get_app_key()
        app_secret = self.config_manager.get_app_secret()
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


    def _save_dropbox_access_token(self, access_token, refresh_token, expires_in=14400):
        preferences = self.config_manager._load_preferences() or {}
        preferences['dropbox_access_token'] = access_token
        preferences['dropbox_refresh_token'] = refresh_token
        preferences['dropbox_token_expiry'] = (datetime.now() + timedelta(seconds=expires_in)).strftime('%Y-%m-%d %H:%M:%S')
        self.config_manager._save_preferences(preferences)


    def _upload_file_to_dropbox(self, local_file_path):
        access_token = self._get_dropbox_access_token()
        if not access_token:
            print("Dropbox access token not found. Please authenticate first.")
            return

        dbx = dropbox.Dropbox(access_token)
        with open(local_file_path, 'rb') as f:
            dbx.files_upload(f.read(), '/' + os.path.basename(local_file_path), mode=WriteMode('overwrite'))
        print(f"Successfully uploaded {os.path.basename(local_file_path)} to Dropbox")


    def _download_file_from_dropbox(self, access_token, dropbox_path, local_path):
        dbx = dropbox.Dropbox(access_token)
        try:
            metadata, res = dbx.files_download(path=dropbox_path)
            with open(local_path, 'wb') as f:
                f.write(res.content)
            print(f"Successfully downloaded {dropbox_path} to {local_path}")
        except dropbox.exceptions.ApiError as e:
            print(f"Error downloading file: {e}")


    def authenticate_dropbox(self, app_key, app_secret):
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
                        local_mod_time = datetime.fromtimestamp(os.path.getmtime(local_file_path), tz=timezone.utc)
                        dropbox_mod_time_utc = entry.client_modified.replace(tzinfo=timezone.utc)

                        if dropbox_mod_time_utc  > local_mod_time:
                            self._download_file_from_dropbox(access_token, dropbox_file_path, local_file_path)
                        else:
                            print(f"Local file '{local_file_path}' is newer. Skipping download.")
                    else:
                        self._download_file_from_dropbox(access_token, dropbox_file_path, local_file_path)
        except dropbox.exceptions.ApiError as e:
            print(f"Error listing files in Dropbox folder: {e}")
