import os
import sys

from steam.steam_id import SteamId


def is_steam_deck():
    """Detect if running on Steam Deck hardware."""
    # Method 1: DMI product name (Jupiter = Deck codename)
    try:
        with open("/sys/class/dmi/id/product_name", "r") as f:
            return "Jupiter" in f.read()
    except:
        pass
    
    # Method 2: DMI product family
    try:
        with open("/sys/class/dmi/id/product_family", "r") as f:
            return "Jupiter" in f.read() or "Steam Deck" in f.read()
    except:
        pass
    
    # Method 3: Check for deck-control binary (exists on Deck)
    try:
        if os.path.exists("/usr/bin/deck-control"):
            return True
    except:
        pass
    
    return False


def find_steam_path_unix():
    """
    Find Steam installation path on Unix-like systems.
    Handles both desktop Linux and Steam Deck.
    """
    home = os.path.expanduser("~")
    
    # Steam Deck-specific paths
    if is_steam_deck():
        deck_paths = [
            os.path.join(home, ".local", "share", "Steam"),  # Deck's primary path
            "/usr/bin/deck-steam",
        ]
        for path in deck_paths:
            if os.path.exists(path):
                # If it's a binary/symlink, get the actual Steam directory
                if os.path.islink(path):
                    real_path = os.path.realpath(path)
                    steam_root = os.path.dirname(real_path)
                    if os.path.exists(os.path.join(steam_root, "steam.sh")):
                        return steam_root
                elif os.path.isdir(path):
                    return path
    
    # Standard Linux paths
    steam_paths = [
        os.path.join(home, ".steam", "steam"),
        os.path.join(home, ".local", "share", "Steam"),
    ]
    
    # Only add /usr/bin/steam as fallback AND verify it's a directory, not just a binary
    try:
        if os.path.isdir("/usr/bin/steam"):
            steam_paths.append("/usr/bin/steam")
        elif os.path.islink("/usr/bin/steam"):
            real_path = os.path.realpath("/usr/bin/steam")
            if os.path.isdir(real_path) and os.path.exists(os.path.join(real_path, "steam.sh")):
                steam_paths.append(real_path)
    except:
        pass
    
    for path in steam_paths:
        if os.path.exists(path):
            return path

    return None


def get_steam_path():
    if sys.platform.startswith('linux'):
        return find_steam_path_unix()
    elif sys.platform.startswith('win'):
        return find_steam_path_windows()


def find_steam_path_windows():
    steam_paths = [
        os.path.join(os.getenv("ProgramFiles(x86)"), "Steam"),
        os.path.join(os.getenv("ProgramFiles"), "Steam"),
        os.path.join(os.getenv("LocalAppData"), "Programs", "Steam")
    ]
    for path in steam_paths:
        if os.path.exists(path):
            return path
    
    # If Steam path is not found in common locations, try the Windows Registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
        steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
        return steam_path
    except Exception as e:
        print("Error accessing Windows Registry:", e)
    
    return None


def get_steam_ids():
    steam_path = get_steam_path()
    if not steam_path:
        return []
    userdata_path = os.path.join(steam_path, 'userdata')
    if not os.path.exists(userdata_path):
        return []
    steam_ids = []
    for user_id in os.listdir(userdata_path):
        steam_ids.append(SteamId(steamid=user_id))
    return steam_ids


def get_grid_path(steam_id: SteamId):
    steam_path = get_steam_path()
    if not steam_path:
        return None
    grid_path = ['userdata', steam_id.get_steamid(), 'config', 'grid']
    return os.path.join(steam_path, *grid_path)


if __name__ == "__main__":
    print("Finding path to Steam.")
    print(f"Is Steam Deck: {is_steam_deck()}")
    print(get_steam_path())
