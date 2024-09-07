import os
import sys
if os.name == 'nt':  # Windows
    import winshell


def start_on_boot(start_on_boot=True):
    if os.name == 'nt':  # Windows
        _start_on_boot_windows(start_on_boot)


def _start_on_boot_windows(start_on_boot):
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    shortcut_path = os.path.join(startup_path, "SteamBeautifier.lnk")
    if start_on_boot:
        _set_start_on_boot_windows(shortcut_path)
    else:
        _delete_windows_startup_lnk(shortcut_path)


def _set_start_on_boot_windows(shortcut_path):
    target = sys.executable
    _create_windows_startup_lnk(target, shortcut_path)


def _create_windows_startup_lnk(target, shortcut_path):
    shortcut = winshell.shortcut(shortcut_path)
    shortcut.path = target
    shortcut.description = "Shortcut to launch Steam Beautifier"
    shortcut.write()


def _delete_windows_startup_lnk(shortcut_path):
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
