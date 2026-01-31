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
        self.session = requests.Session()
        self.session.auth = self.auth


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
            
            # Check if the collection exists
            response = self.session.request('PROPFIND', folder_url, headers={'Depth': '0'})

            # 404 means it doesn't exist, so we need to create it.
            if response.status_code == 404:
                print(f"Folder '{current_path}' does not exist. Creating it...")
                mkcol_response = self.session.request('MKCOL', folder_url)
                
                # 201 Created is success.
                # 405 Method Not Allowed often means it was created by another process
                # between our PROPFIND and MKCOL calls (a race condition), so we treat it as success.
                if mkcol_response.status_code in (201, 405):
                    pass
                    # print(f"Folder '{current_path}' created successfully.")
                else:
                    # print(f"Failed to create folder '{current_path}': {mkcol_response.status_code} {mkcol_response.text}")
                    # You might want to raise an exception here to stop the script
                    raise Exception(f"Failed to create folder '{current_path}': {mkcol_response.status_code}")
            
            # 200 or 207 means it already exists.
            elif response.status_code in (200, 207):
                pass
                # print(f"Folder '{current_path}' already exists.")
            
            # Handle other unexpected errors
            else:
                # print(f"Unexpected response ({response.status_code}) when checking folder '{current_path}'.")
                # print(response.text)
                raise Exception(f"Failed to check/create folder '{current_path}': {response.status_code}")


    def get_remote_file_modtime(self, remote_file):
        """
        Retrieve the last modification time of the remote file using a PROPFIND request.
        Returns the modification timestamp (seconds since epoch) or None if the file doesn't exist.
        """
        headers = {'Depth': '0'}
        remote_url = self._get_remote_url(remote_file)
        response = self.session.request('PROPFIND', remote_url, headers=headers)
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
            # print(f"Unexpected PROPFIND response for {remote_url}: {response.status_code} - {response.text}")
            return None


    def list_remote_files(self, remote_folder):
        """
        Lists the files in the remote folder by performing a PROPFIND with Depth 1.
        Returns a dictionary mapping filenames to their last modification timestamps.
        """
        folder_url = self._get_remote_url(remote_folder)
        headers = {'Depth': '1'}
        response = self.session.request('PROPFIND', folder_url, headers=headers)
        files = {}
        if response.status_code not in [200, 207]:
            if response.status_code == 404:
                return {} # Folder doesn't exist, so it's empty
            if response.status_code == 401:
                raise Exception("Authentication failed (401). Check credentials.")
            raise Exception(f"Failed to list files: {response.status_code}")
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
            response = self.session.put(remote_url, data=file_contents)
            # if response.status_code in [200, 201, 204]:
            #     print(f"Uploaded successfully to {remote_url}")
            if response.status_code not in [200, 201, 204]:
                raise Exception(f"Failed to upload. Status: {response.status_code}")
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
            response = self.session.get(remote_url)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 404:
                print(f"File not found: {remote_url}")
                return None
            else:
                raise Exception(f"Failed to download. Status: {response.status_code}")
        except Exception as e:
            print(f"Error downloading: {e}")
