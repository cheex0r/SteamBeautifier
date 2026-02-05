import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock requests before importing
sys.modules['requests'] = MagicMock()

from cloud.steam_grid_sync_manager import SteamGridSyncManager
from cloud.constants import STEAM_GRID_SYNC_DIR, NON_STEAM_DIR

class TestSteamGridSyncConflict(unittest.TestCase):
    def setUp(self):
        self.mock_cloud_manager = MagicMock()
        self.mock_cloud_manager.list_remote_files.return_value = {}
        self.manager = SteamGridSyncManager(self.mock_cloud_manager, {})
        self.local_dir = "test_dir"

    @patch('os.listdir')
    @patch('os.path.isfile')
    @patch('os.path.join')
    @patch('os.path.getmtime')
    @patch('os.path.getctime')
    @patch('os.remove')
    def test_conflict_local_newer(self, mock_remove, mock_ctime, mock_mtime, mock_join, mock_isfile, mock_listdir):
        # Scenario: 
        # Remote: 123.jpg (Old)
        # Local: 123.png (New)
        # Expectation: SKIP download of 123.jpg. 123.png is kept.
        
        remote_filename = "123.jpg"
        remote_mod_time = 1000
        
        local_conflict_filename = "123.png"
        local_mod_time = 2000 # Newer
        
        # Setup mocks
        self.mock_cloud_manager.list_remote_files.return_value = {remote_filename: remote_mod_time}
        mock_listdir.return_value = [local_conflict_filename] # Only 123.png exists locally
        mock_join.side_effect = lambda a, b: f"{a}/{b}"
        
        mock_mtime.return_value = local_mod_time
        mock_ctime.return_value = local_mod_time
        
        # We need to expose the internal process function or mock executor to run inline
        # Since we modified download_steam_games_grid, we can just call it
        # However, it uses ThreadPoolExecutor. We'll mock that to run immediately.
        
        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
            # Create a mock context manager that yields a mock executor
            instance_mock = MagicMock()
            mock_executor.return_value.__enter__.return_value = instance_mock
            
            # Setup submit to run the function immediately (simplified)
            # Actually easier to just extract the inner function or reliance on implementation details
            # Let's trust the logic structure and verify via behavior if possible.
            # But since inner function `process_download_steam` is not exposed... 
            # We will rely on correct invocation.
            
            # Wait, since process_download_steam is inner, we can't test it directly easily without
            # refactoring or running the whole method.
            # Let's run the whole method and capture the calls.
            
            # We need to make sure `submit` actually runs the callback.
            def side_effect_submit(fn, *args, **kwargs):
                fn(*args, **kwargs) # Run immediately
                return MagicMock()
            
            instance_mock.submit.side_effect = side_effect_submit
            
            self.manager.download_steam_games_grid(self.local_dir)
            
            # Verify:
            # download_file should NOT be called for 123.jpg
            self.mock_cloud_manager.download_file.assert_not_called()
            
            # Verify os.remove NOT called (we don't delete local new file)
            mock_remove.assert_not_called()
            
            print("\n[Passed] test_conflict_local_newer: Skipped download of old remote .jpg")

    @patch('os.listdir')
    @patch('os.path.isfile')
    @patch('os.path.join')
    @patch('os.path.getmtime')
    @patch('os.path.getctime')
    @patch('os.remove')
    def test_conflict_local_older(self, mock_remove, mock_ctime, mock_mtime, mock_join, mock_isfile, mock_listdir):
        # Scenario: 
        # Remote: 123.jpg (New)
        # Local: 123.png (Old)
        # Expectation: DELETE 123.png, DOWNLOAD 123.jpg
        
        remote_filename = "123.jpg"
        remote_mod_time = 2000 # Newer
        
        local_conflict_filename = "123.png"
        local_mod_time = 1000 # Older
        
        self.mock_cloud_manager.list_remote_files.return_value = {remote_filename: remote_mod_time}
        mock_listdir.return_value = [local_conflict_filename]
        mock_join.side_effect = lambda a, b: f"{a}/{b}"
        
        mock_mtime.return_value = local_mod_time
        mock_ctime.return_value = local_mod_time
        
        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
            instance_mock = MagicMock()
            mock_executor.return_value.__enter__.return_value = instance_mock
            
            def side_effect_submit(fn, *args, **kwargs):
                fn(*args, **kwargs)
                return MagicMock()
            instance_mock.submit.side_effect = side_effect_submit
            
            self.manager.download_steam_games_grid(self.local_dir)
            
            # Verify:
            # os.remove SHOULD be called for 123.png
            mock_remove.assert_called_with(f"{self.local_dir}/{local_conflict_filename}")
            
            # download_file SHOULD be called for 123.jpg
            self.mock_cloud_manager.download_file.assert_called_with(
                f"{STEAM_GRID_SYNC_DIR}/{remote_filename}",
                f"{self.local_dir}/{remote_filename}"
            )
            
            print("\n[Passed] test_conflict_local_older: Deleted local .png, Downloaded remote .jpg")

if __name__ == '__main__':
    unittest.main()
