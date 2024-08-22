import os
import platform
import sys
if platform.system() == "Windows":
    import winshell

class StartOnBootManager:
    @staticmethod
    def start_on_boot(start_on_boot=True):
        if platform.system() == "Windows":
            # Get the path to the startup folder
            startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')

            # Print the path
            print("Startup folder:", startup_path)

        manager = StartOnBootManager()
        if os.name == 'nt':  # Windows
            manager._start_on_boot_windows(start_on_boot)

    @staticmethod
    def _start_on_boot_windows(self, start_on_boot):
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        shortcut_path = os.path.join(startup_path, "SteamBeautifier.lnk")
        if start_on_boot:
            self._set_start_on_boot_windows(shortcut_path)
        else:
            self._delete_windows_startup_lnk(shortcut_path)

    @staticmethod
    def _set_start_on_boot_windows(self, shortcut_path):
        target = sys.executable
        self._create_windows_startup_lnk(target, shortcut_path)

    @staticmethod
    def _create_windows_startup_lnk(self, target, shortcut_path):
        shortcut = winshell.shortcut(shortcut_path)
        shortcut.path = target
        shortcut.description = "Shortcut to launch Steam Beautifier"
        shortcut.write()

    @staticmethod
    def _delete_windows_startup_lnk(self, shortcut_path):
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

# Example usage
if __name__ == "__main__":
    StartOnBootManager.start_on_boot(start_on_boot=True)
