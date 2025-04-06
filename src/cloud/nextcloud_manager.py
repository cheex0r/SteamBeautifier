import os
import urllib.parse
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

class NextcloudManager:
    def __init__(self, base_url, username, password):
        """
        Initialize the NextcloudManager.

        Args:
            base_url (str): The base URL of your Nextcloud instance 
                            (e.g., 'https://nextcloud.example.com').
            username (str): The Nextcloud username (or email, if that's your login).
            password (str): The Nextcloud password.
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.auth = (username, password)

    def _get_remote_file_url(self, remote_folder, filename):
        """
        Construct the full URL for a remote file.
        """
        encoded_user = urllib.parse.quote(self.username, safe='')
        remote_folder = remote_folder.strip('/')
        encoded_folder = urllib.parse.quote(remote_folder, safe='/')
        return f"{self.base_url}/remote.php/dav/files/{encoded_user}/{encoded_folder}/{filename}"

    def _get_remote_folder_url(self, remote_folder):
        """
        Construct the full URL for the remote folder.
        """
        encoded_user = urllib.parse.quote(self.username, safe='')
        remote_folder = remote_folder.strip('/')
        encoded_folder = urllib.parse.quote(remote_folder, safe='/')
        return f"{self.base_url}/remote.php/dav/files/{encoded_user}/{encoded_folder}"

    def _ensure_remote_folder(self, remote_folder):
        """
        Ensure that the remote folder (and its parent directories) exists on Nextcloud.
        If a folder does not exist, it is created.
        """
        parts = remote_folder.strip('/').split('/')
        current_path = ""
        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            folder_url = self._get_remote_folder_url(current_path)
            headers = {'Depth': '0'}
            response = requests.request('PROPFIND', folder_url, auth=self.auth, headers=headers)
            if response.status_code in [200, 207]:
                print(f"Folder '{current_path}' exists.")
            elif response.status_code == 404:
                print(f"Folder '{current_path}' does not exist. Creating it...")
                mkcol_response = requests.request('MKCOL', folder_url, auth=self.auth)
                if mkcol_response.status_code in (201, 405):  # 405 might occur if it’s created concurrently
                    print(f"Folder '{current_path}' created successfully.")
                else:
                    print(f"Failed to create folder '{current_path}': {mkcol_response.status_code} {mkcol_response.text}")
            else:
                print(f"Unexpected response ({response.status_code}) when checking folder '{current_path}'.")

    def _get_remote_file_modtime(self, remote_url):
        """
        Retrieve the last modification time of the remote file using a PROPFIND request.
        Returns the modification timestamp (seconds since epoch) or None if the file doesn't exist.
        """
        headers = {'Depth': '0'}
        response = requests.request('PROPFIND', remote_url, auth=self.auth, headers=headers)
        if response.status_code in [200, 207]:
            try:
                root = ET.fromstring(response.content)
                ns = {'d': 'DAV:'}
                mod_elem = root.find('.//d:getlastmodified', ns)
                if mod_elem is not None and mod_elem.text:
                    remote_dt = parsedate_to_datetime(mod_elem.text)
                    return remote_dt.timestamp()
            except Exception as e:
                print(f"Error parsing PROPFIND response for {remote_url}: {e}")
                return None
        elif response.status_code == 404:
            return None
        else:
            print(f"Unexpected PROPFIND response for {remote_url}: {response.status_code} - {response.text}")
            return None

    def _list_remote_files(self, remote_folder):
        """
        Lists the files in the remote folder by performing a PROPFIND with Depth 1.
        Returns a dictionary mapping filenames to their last modification timestamps.
        """
        folder_url = self._get_remote_folder_url(remote_folder)
        headers = {'Depth': '1'}
        response = requests.request('PROPFIND', folder_url, auth=self.auth, headers=headers)
        files = {}
        if response.status_code not in [200, 207]:
            print(f"Failed to list remote files in '{remote_folder}': {response.status_code} {response.text}")
            return files
        try:
            root = ET.fromstring(response.content)
            ns = {'d': 'DAV:'}
            # Each <d:response> represents either the folder itself or a file/subfolder
            for response_elem in root.findall('d:response', ns):
                href_elem = response_elem.find('d:href', ns)
                if href_elem is None:
                    continue
                href = href_elem.text
                # Extract the file name from the URL path
                parsed = urllib.parse.urlparse(href)
                path = parsed.path
                filename = os.path.basename(path.rstrip('/'))
                # Decode the filename to convert %20 back to spaces
                filename = urllib.parse.unquote(filename)
                # Skip the folder itself (empty filename)
                if not filename:
                    continue
                mod_elem = response_elem.find('.//d:getlastmodified', ns)
                if mod_elem is not None and mod_elem.text:
                    remote_dt = parsedate_to_datetime(mod_elem.text)
                    mod_time = remote_dt.timestamp()
                else:
                    mod_time = None
                files[filename] = mod_time
        except Exception as e:
            print(f"Error parsing remote folder listing: {e}")
        return files


    def upload_all_files(self, local_folder, remote_folder):
        """
        Uploads files from a local directory to a remote directory in Nextcloud,
        but only if the local file is newer than the remote version or if the remote file doesn't exist.
        """
        # Ensure the target remote folder exists
        self._ensure_remote_folder(remote_folder)
        for filename in os.listdir(local_folder):
            local_path = os.path.join(local_folder, filename)
            if not os.path.isfile(local_path):
                continue  # Skip if it's not a file
            remote_url = self._get_remote_file_url(remote_folder, filename)
            local_mod_time = os.path.getmtime(local_path)
            remote_mod_time = self._get_remote_file_modtime(remote_url)
            if remote_mod_time is None:
                print(f"Remote file '{filename}' does not exist. Uploading...")
            elif local_mod_time > remote_mod_time:
                print(f"Local file '{filename}' is newer (local: {local_mod_time}, remote: {remote_mod_time}). Uploading...")
            else:
                print(f"Skipping '{filename}' as remote file is up-to-date.")
                continue
            with open(local_path, 'rb') as f:
                file_data = f.read()
            try:
                response = requests.put(remote_url, data=file_data, auth=self.auth)
                if response.status_code in [200, 201, 204]:
                    print(f"Uploaded '{filename}' successfully to {remote_url}")
                else:
                    print(f"Failed to upload '{filename}'. Status: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error uploading '{filename}': {e}")

    def download_all_files(self, local_folder, remote_folder):
        """
        Downloads files from a remote Nextcloud directory to a local folder,
        but only if the remote file is newer than the local version or if the local file doesn't exist.
        """
        # Ensure the local folder exists
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)

        remote_files = self._list_remote_files(remote_folder)
        for filename, remote_mod_time in remote_files.items():
            local_path = os.path.join(local_folder, filename)
            # If the local file exists, get its modification time; otherwise, assume it doesn't exist.
            local_mod_time = os.path.getmtime(local_path) if os.path.exists(local_path) else 0

            if remote_mod_time is None:
                print(f"Could not determine modification time for remote file '{filename}', skipping download.")
                continue

            if local_mod_time < remote_mod_time:
                remote_url = self._get_remote_file_url(remote_folder, filename)
                print(f"Downloading '{filename}' (remote: {remote_mod_time}, local: {local_mod_time})...")
                try:
                    response = requests.get(remote_url, auth=self.auth)
                    if response.status_code == 200:
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                        print(f"Downloaded '{filename}' successfully.")
                    else:
                        print(f"Failed to download '{filename}'. Status: {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"Error downloading '{filename}': {e}")
            else:
                print(f"Skipping '{filename}' as local file is up-to-date (local: {local_mod_time}, remote: {remote_mod_time}).")


# Main function to demonstrate usage. User name and password should be prompted for via CLI
def main():
    username = input("Enter your Nextcloud username: ")
    password = input("Enter your Nextcloud password: ")
    
    base_url = "https://cloud.cheesman.xyz"
    local_folder = "D:\\Downloads\\NextcloudTemp"
    remote_folder = "SteamBeautifier/SteamGridDB/SteamGridDB/Images/Grid"

    manager = NextcloudManager(base_url, username, password)
    manager.download_all_files(local_folder, remote_folder)
    print("Download completed.")
    manager.upload_all_files(local_folder, remote_folder)
    print("Upload completed.")

if __name__ == "__main__":
    main()