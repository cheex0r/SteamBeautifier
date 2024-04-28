import os
import sys

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

def find_steam_path_unix():
    home = os.path.expanduser("~")
    steam_paths = [
        os.path.join(home, ".steam", "steam"),
        os.path.join(home, ".local", "share", "Steam"),
        "/usr/bin/steam"  # Default install path on some Linux distributions
    ]
    for path in steam_paths:
        if os.path.exists(path):
            return path

    return None
    
if __name__ == "__main__":
    print("Finding path to Steam.")
    # If the script is executed directly, call the main function
    print(get_steam_path())
