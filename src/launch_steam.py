import os
import platform
import sys
import subprocess

from steam_directory_finder import get_steam_path

def launch_steam(is_bigpicture=False):
    if platform.system() == 'Windows':
        launch_steam_windows(is_bigpicture)
    else:
        launch_steam_linux(is_bigpicture)


def launch_steam_windows(is_bigpicture=False):
    print("Launching Steam on Windows")
    steam_path = get_steam_path()
    # Determine the path to the Steam executable based on the platform
    if platform.system() == 'Windows':
        steam_exe = 'Steam.exe'
    else:
        steam_exe = 'steam'

    steam_executable_path = os.path.join(steam_path, steam_exe)

    # Ensure the Steam executable file has execute permissions
    try:
        os.chmod(steam_executable_path, 0o755)  # Add execute permission
    except Exception as e:
        print("Error changing permissions for Steam executable:", e)
        return

    # Add command-line arguments to launch Steam in Big Picture Mode
    args = [steam_executable_path]
    if is_bigpicture:
        args.append('-bigpicture')

    # Launch Steam using subprocess
    try:
        subprocess.Popen(args)
        print("Steam launched successfully")
    except Exception as e:
        print("An error occurred while launching Steam:", e)

import subprocess
import sys

def launch_steam_linux(is_bigpicture=False):
    print("Launching Steam on Linux")
    # Add command-line arguments to launch Steam in Big Picture Mode
    args = ['steam']
    if is_bigpicture:
        args.append('-bigpicture')

    # Launch Steam using subprocess
    try:
        subprocess.Popen(args)
        print("Steam launched successfully")
    except Exception as e:
        print("An error occurred while launching Steam:", e)

if __name__ == "__main__":
    is_bigpicture = "--bigpicture" in sys.argv
    # Call the function to launch Steam
    launch_steam(is_bigpicture)
