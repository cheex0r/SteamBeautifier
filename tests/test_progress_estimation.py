import unittest
from unittest.mock import patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestFormatTimeRemaining(unittest.TestCase):
    """Test the format_time_remaining helper function."""

    def test_seconds_only(self):
        """Test formatting for times less than 60 seconds."""
        from steam.steam_image_downloader import format_time_remaining
        
        self.assertEqual(format_time_remaining(30), "30s")
        self.assertEqual(format_time_remaining(59), "59s")

    def test_minutes_seconds(self):
        """Test formatting for times between 1-59 minutes."""
        from steam.steam_image_downloader import format_time_remaining
        
        self.assertEqual(format_time_remaining(90), "1m 30s")
        self.assertEqual(format_time_remaining(120), "2m 0s")
        self.assertEqual(format_time_remaining(3599), "59m 59s")

    def test_hours_minutes(self):
        """Test formatting for times 1 hour or more."""
        from steam.steam_image_downloader import format_time_remaining
        
        self.assertEqual(format_time_remaining(3600), "1h 0m")
        self.assertEqual(format_time_remaining(3660), "1h 1m")
        self.assertEqual(format_time_remaining(7200), "2h 0m")
        self.assertEqual(format_time_remaining(7500), "2h 5m")

    def test_large_times(self):
        """Test formatting for very large times."""
        from steam.steam_image_downloader import format_time_remaining
        
        self.assertEqual(format_time_remaining(86400), "24h 0m")
        self.assertEqual(format_time_remaining(90000), "25h 0m")


class TestThreadPoolExecutorBatchSize(unittest.TestCase):
    """Test that ThreadPoolExecutor uses batch size of 25."""

    def test_source_code_has_max_workers_25(self):
        """Verify ThreadPoolExecutor is called with max_workers=25 in source code."""
        import re
        import os
        
        # Read the source files (use absolute paths)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dropbox_manager_path = os.path.join(script_dir, '..', 'src', 'cloud', 'dropbox_manager.py')
        sync_manager_path = os.path.join(script_dir, '..', 'src', 'cloud', 'steam_grid_sync_manager.py')
        
        with open(dropbox_manager_path, 'r') as f:
            dropbox_content = f.read()
        
        with open(sync_manager_path, 'r') as f:
            sync_content = f.read()
        
        # Check for ThreadPoolExecutor with max_workers=25
        dropbox_has_max_workers = re.search(r'ThreadPoolExecutor\(max_workers=25\)', dropbox_content) is not None
        sync_has_max_workers = re.search(r'ThreadPoolExecutor\(max_workers=25\)', sync_content) is not None
        
        self.assertTrue(dropbox_has_max_workers, 
                       "dropbox_manager.py should use max_workers=25")
        self.assertTrue(sync_has_max_workers,
                       "steam_grid_sync_manager.py should use max_workers=25")


if __name__ == '__main__':
    unittest.main()
