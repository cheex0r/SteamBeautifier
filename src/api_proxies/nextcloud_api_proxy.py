import os
import urllib.parse
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime


class NextcloudApiProxy:
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


    def _get_remote_url(self, remote_path):
        """
        Construct the full URL for the remote folder.
        """
        encoded_user = urllib.parse.quote(self.username, safe='')
        remote_path = remote_path.strip('/')
        encoded_folder = urllib.parse.quote(remote_path, safe='/')
        return f"{self.base_url}/remote.php/dav/files/{encoded_user}/{encoded_folder}"


    def ensure_remote_folder(self, remote_folder):
        """
        Ensure that the remote folder (and its parent directories) exists on Nextcloud.
        If a folder does not exist, it is created.
        """
        parts = remote_folder.strip('/').split('/')
        current_path = ""
        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            folder_url = self._get_remote_url(current_path)
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


    def get_remote_file_modtime(self, remote_file):
        """
        Retrieve the last modification time of the remote file using a PROPFIND request.
        Returns the modification timestamp (seconds since epoch) or None if the file doesn't exist.
        """
        headers = {'Depth': '0'}
        remote_url = self._get_remote_url(remote_file)
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


    def list_remote_files(self, remote_folder):
        """
        Lists the files in the remote folder by performing a PROPFIND with Depth 1.
        Returns a dictionary mapping filenames to their last modification timestamps.
        """
        folder_url = self._get_remote_url(remote_folder)
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


    def upload_file(self, file_contents, remote_file):
        """
        Upload file contents to Nextcloud.

        Args:
            file_contents (bytes): The content of the file.
            remote_file (str): The remote file path.
        """
        remote_url = self._get_remote_url(remote_file)
        
        try:
            response = requests.put(remote_url, data=file_contents, auth=self.auth)
            if response.status_code in [200, 201, 204]:
                print(f"Uploaded successfully to {remote_url}")
            else:
                print(f"Failed to upload. Status: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error uploading: {e}")


    def download_file(self, remote_file):
        """
        Download a file from Nextcloud.

        Args:
            remote_file (str): The remote file path.
            local_path (str): The local path where the file will be saved.
        """
        remote_url = self._get_remote_url(remote_file)
        try:
            response = requests.get(remote_url, auth=self.auth)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 404:
                print(f"File not found: {remote_url}")
                return None
            else:
                print(f"Failed to download. Status: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error downloading: {e}")
