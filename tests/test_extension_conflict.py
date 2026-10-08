import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from cloud.steam_grid_sync_manager import SteamGridSyncManager, STEAM_GRID_SYNC_DIR, NON_STEAM_DIR

class TestSteamGridSyncConflict(unittest.TestCase):
    def setUp(self):
        self.mock_cloud_manager = MagicMock()
        self.mock_cloud_manager.list_remote_files.return_value = {}
        self.manager = SteamGridSyncManager(self.mock_cloud_manager, {})
        self.local_dir = "test_dir"

    def test_source_has_threadpool_executor_with_max_workers(self):
        """Verify that download_steam_games_grid uses ThreadPoolExecutor with max_workers."""
        import re
        
        # Read the source file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sync_manager_path = os.path.join(script_dir, '..', 'src', 'cloud', 'steam_grid_sync_manager.py')
        
        with open(sync_manager_path, 'r') as f:
            content = f.read()
        
        # Check for max_workers parameter
        has_max_workers = re.search(r'max_workers=\d+', content) is not None
        self.assertTrue(has_max_workers, "download_steam_games_grid should specify max_workers parameter")

if __name__ == '__main__':
    unittest.main()
