import os

from api_proxies.nextcloud_api_proxy import NextcloudApiProxy

class NextcloudManager:
    def __init__(self, api_proxy: NextcloudApiProxy, base_folder=""):
        """
        Initialize the NextcloudManager.

        Args:
            api_proxy (NextcloudApiProxy): Instance to perform Nextcloud operations.
            base_folder (str): The base folder in Nextcloud to use for uploads/downloads.
        """
        self.api_proxy = api_proxy
        self.base_folder = base_folder.strip('/')


    def _combine_folder(self, remote_folder):
        """
        Combine the base_folder with the remote_folder passed in.
        """
        remote_folder = remote_folder.strip('/')
        if self.base_folder:
            # If a remote_folder is provided, append it to base_folder
            if remote_folder:
                return f"{self.base_folder}/{remote_folder}"
            else:
                return self.base_folder
        return remote_folder
    

    def ensure_remote_folder(self, remote_folder):
        """
        Ensure that the remote folder exists on Nextcloud. If it does not exist, it is created.

        Args:
            remote_folder (str): The remote folder path to check/create.
        """
        remote_folder = self._combine_folder(remote_folder)
        self.api_proxy.ensure_remote_folder(remote_folder)


    def upload_file(self, local_file, remote_file, remote_mod_time=-1.0):
        """
        Upload a single file to Nextcloud if newer than the remote version or if the remote file doesn't exist.
        This method checks the modification time of the local file against the remote file.

        Args:
            local_file (str): The path to the local file.
            remote_file (str): The remote file path, including the folder and file name.
            remote_mod_time (float, optional): Known remote modification time (or None if missing). 
                                               Defaults to -1.0, which forces a lookup.
        """
        remote_file = self._combine_folder(remote_file)
        local_mod_time = os.path.getmtime(local_file)
        local_ctime = os.path.getctime(local_file)
        
        if remote_mod_time == -1.0:
            remote_mod_time = self.api_proxy.get_remote_file_modtime(remote_file)

        if remote_mod_time is None:
            pass
            # print(f"Remote file '{remote_file}' does not exist. Uploading...")
        elif abs(local_mod_time - remote_mod_time) < 2:
             # Files are effectively in sync (timestamp match)
             return
        elif local_mod_time > remote_mod_time + 2 or local_ctime > remote_mod_time + 2:
            pass
            # print(f"Local file '{local_file}' is newer (Mtime or Ctime). Uploading...")
        else:
            pass
            # print(f"Skipping '{local_file}' as remote file is up-to-date.")
            return

        with open(local_file, 'rb') as f:
            file_data = f.read()

        self.api_proxy.upload_file(file_data, remote_file)


    def download_file(self, remote_file, local_file):
        """
        Download a single file from Nextcloud if the remote version is newer than the local version,
        or if the local file doesn't exist.
        
        Args:
            remote_file (str): The remote file path (relative to the cloud folder).
            local_file (str): The full path where the file should be saved locally.
        """
        # Combine the remote file path with the cloud folder.
        # print(f"Ensuring remote folder exists for '{remote_file}'...")
        remote_file_path = self._combine_folder(remote_file)
        
        # Get the remote file modification time.
        remote_mod_time = self.api_proxy.get_remote_file_modtime(remote_file_path)
        if remote_mod_time is None:
            # print(f"Remote file '{remote_file_path}' does not exist. Skipping download.")
            return

        # Check if the local file exists and get its modification time.
        if os.path.exists(local_file):
            local_mod_time = os.path.getmtime(local_file)
            local_ctime = os.path.getctime(local_file)
        else:
            local_mod_time = None
            local_ctime = None

        # If the local file exists and is up-to-date, skip the download.
        if local_mod_time is not None:
             if local_mod_time >= remote_mod_time or local_ctime >= remote_mod_time:
                pass 
                # print(f"Local file '{local_file}' is up-to-date. Skipping download.")
                return

        # print(f"Downloading '{remote_file_path}' to '{local_file}'...")
        # Download the file content.
        file_data = self.api_proxy.download_file(remote_file_path)

        # Ensure the local destination directory exists before writing the file.
        local_dir = os.path.dirname(local_file)
        os.makedirs(local_dir, exist_ok=True)
            
        # Write the file content to disk.
        with open(local_file, 'wb') as f:
            f.write(file_data)
        
        os.utime(local_file, (remote_mod_time, remote_mod_time))


    def list_remote_files(self, remote_folder):
        """
        List all files in the specified remote folder.

        Args:
            remote_folder (str): The remote folder path.

        Returns:
            list: A list of file names in the remote folder.
        """
        remote_folder = self._combine_folder(remote_folder)
        return self.api_proxy.list_remote_files(remote_folder)


    def delete_file(self, remote_file):
        """
        Delete a remote file.
        
        Args:
            remote_file (str): The remote file path relative to base.
        """
        remote_file_path = self._combine_folder(remote_file)
        self.api_proxy.delete_file(remote_file_path)

