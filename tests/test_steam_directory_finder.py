import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestIsSteamDeck(unittest.TestCase):
    """Test the is_steam_deck function."""

    def test_non_deck_system(self):
        """Test that non-Deck systems return False."""
        from steam.steam_directory_finder import is_steam_deck
        
        # This should return False on non-Deck systems
        result = is_steam_deck()
        self.assertFalse(result, "Non-Deck systems should return False")


class TestFindSteamPathUnix(unittest.TestCase):
    """Test the find_steam_path_unix function."""

    def test_finds_valid_steam_path(self):
        """Test that valid Steam paths are found."""
        from steam.steam_directory_finder import find_steam_path_unix
        
        # On systems with Steam, this should return a path
        # On systems without Steam, this should return None
        result = find_steam_path_unix()
        
        # Just verify it returns None or a string (path)
        self.assertTrue(result is None or isinstance(result, str), 
                       "find_steam_path_unix should return None or string path")


class TestGetSteamPath(unittest.TestCase):
    """Test the get_steam_path function."""

    def test_returns_valid_path(self):
        """Test that get_steam_path returns a valid path or None."""
        from steam.steam_directory_finder import get_steam_path
        
        result = get_steam_path()
        
        # Just verify it returns None or a string (path)
        self.assertTrue(result is None or isinstance(result, str),
                       "get_steam_path should return None or string path")


if __name__ == '__main__':
    unittest.main()
