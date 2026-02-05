import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock requests before importing modules that use it
sys.modules['requests'] = MagicMock()

from cloud.nextcloud_manager import NextcloudManager

class TestNextcloudSyncLogic(unittest.TestCase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.manager = NextcloudManager(self.mock_api, "base")
        self.local_file = "test_dir/test_file.jpg"
        self.remote_file = "test_file.jpg"

    @patch('os.path.exists')
    @patch('os.path.getmtime')
    @patch('os.path.getctime')
    def test_download_skip_logic_fix(self, mock_ctime, mock_mtime, mock_exists):
        # Setup: Remote file is "New" (e.g. 1000)
        # Local file is "Old" modification (500) BUT "New" creation (1001) - mimicking the copy scenario
        
        remote_time = 1000
        local_mtime_val = 500
        local_ctime_val = 2000 # Newer than remote
        
        mock_exists.return_value = True
        mock_mtime.return_value = local_mtime_val
        mock_ctime.return_value = local_ctime_val
        self.mock_api.get_remote_file_modtime.return_value = remote_time
        
        # Action
        self.manager.download_file(self.remote_file, self.local_file)
        
        # Assert
        # Should NOT call download_file on api because local Ctime is newer
        self.mock_api.download_file.assert_not_called()
        print("\n[Passed] test_download_skip_logic_fix: Skipped download because local ctime was newer")

    @patch('os.path.exists')
    @patch('os.path.getmtime')
    @patch('os.path.getctime')
    def test_download_standard_logic(self, mock_ctime, mock_mtime, mock_exists):
        # Setup: Remote file is New (1000)
        # Local file is Old (500) and Old Ctime (500)
        
        remote_time = 1000
        local_mtime_val = 500
        local_ctime_val = 500
        
        mock_exists.return_value = True
        mock_mtime.return_value = local_mtime_val
        mock_ctime.return_value = local_ctime_val
        self.mock_api.get_remote_file_modtime.return_value = remote_time
        self.mock_api.download_file.return_value = b"data"
        
        # Action
        self.manager.download_file(self.remote_file, self.local_file)
        
        # Assert
        # Should call download_file
        self.mock_api.download_file.assert_called_once()
        print("\n[Passed] test_download_standard_logic: Downloaded because local was older")

    @patch('os.path.getmtime')
    @patch('os.path.getctime')
    def test_upload_logic_fix(self, mock_ctime, mock_mtime):
        # Setup: Remote file is 1000
        # Local file is 500 mtime (Old), but 2000 ctime (New)
        
        remote_time = 1000
        local_mtime_val = 500
        local_ctime_val = 2000
        
        mock_mtime.return_value = local_mtime_val
        mock_ctime.return_value = local_ctime_val
        # Mock file read
        with patch('builtins.open', unittest.mock.mock_open(read_data=b"data")):
            self.manager.upload_file(self.local_file, self.remote_file, remote_mod_time=remote_time)
            
        # Assert
        self.mock_api.upload_file.assert_called_once()
        print("\n[Passed] test_upload_logic_fix: Uploaded because local ctime was newer")

if __name__ == '__main__':
    unittest.main()
