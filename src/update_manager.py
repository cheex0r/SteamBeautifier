import os
import sys
import subprocess
import requests
import platform
import stat
from packaging import version
from rich.console import Console

GITHUB_REPO = "cheex0r/SteamBeautifier"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

class UpdateManager:
    def __init__(self, current_version, console=None):
        self.current_version = current_version
        self.console = console or Console()

    def check_for_updates(self):
        """
        Checks for updates on GitHub.
        Returns the new version string if an update is available, otherwise None.
        """
        try:
            response = requests.get(GITHUB_API_URL, timeout=5)
            response.raise_for_status()
            latest_release = response.json()
            latest_version_tag = latest_release.get("tag_name", "").lstrip("v")
            
            if not latest_version_tag:
                return None

            if version.parse(latest_version_tag) > version.parse(self.current_version):
                return latest_release
            
            return None
        except Exception as e:
            self.console.print(f"[red]Error checking for updates: {e}[/red]")
            return None

    def perform_update(self, release_data):
        """
        Downloads the new executable and replaces the current one.
        """
        assets = release_data.get("assets", [])
        download_url = None
        for asset in assets:
            if platform.system() == "Windows":
                 if asset["name"] == "steam_beautifier.exe":
                    download_url = asset["browser_download_url"]
                    break
            else: # Linux/Mac
                if asset["name"] == "steam_beautifier":
                    download_url = asset["browser_download_url"]
                    break
        
        if not download_url:
            self.console.print("[red]Update found, but no suitable executable asset found in the release.[/red]")
            return False

        self.console.print(f"[green]Downloading update from {download_url}...[/green]")
        
        try:
            # Download new executable
            new_exe_path = sys.executable + ".new"
            if platform.system() != "Windows":
                 # On Linux, the executable name might not have an extension, but sys.executable should be correct.
                 pass
            
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(new_exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Make executable on Linux/Unix
            if platform.system() != "Windows":
                st = os.stat(new_exe_path)
                os.chmod(new_exe_path, st.st_mode | stat.S_IEXEC)

            self.console.print("[green]Download complete. Restarting to apply update...[/green]")
            
            # Create batch script to swap files and restart
            self._restart_and_swap(new_exe_path)
            return True
            
        except Exception as e:
            self.console.print(f"[red]Failed to download update: {e}[/red]")
            if os.path.exists(new_exe_path):
                os.remove(new_exe_path)
            return False

    def _restart_and_swap(self, new_exe_path):
        current_exe = sys.executable
        
        if platform.system() == "Windows":
            batch_script_path = "update.bat"
            script_content = f"""
@echo off
timeout /t 2 /nobreak > NUL
:loop
tasklist | find "{os.path.basename(current_exe)}" > NUL
if not errorlevel 1 (
    timeout /t 1 /nobreak > NUL
    goto loop
)
move /y "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
            with open(batch_script_path, "w") as f:
                f.write(script_content)
                
            subprocess.Popen([batch_script_path], shell=True)
            sys.exit(0)
        
        else: # Linux
            update_script_path = "update.sh"
            # Linux script:
            # 1. Wait for PID to close (optional, or just sleep)
            # 2. Move new -> current
            # 3. Relaunch (requires user to potentialy authenticate if system-wide? Assume user-local for now)
            # Warning: If running as service, relaunching might detach from service controller.
            # Ideally we should just exit and let systemd restart it if configured. 
            # But the requirement is "automatic update", implying seamlessness.
            # We will try to exec the new one.
            
            script_content = f"""#!/bin/bash
sleep 2
mv "{new_exe_path}" "{current_exe}"
chmod +x "{current_exe}"
"{current_exe}" &
rm "$0"
"""
            with open(update_script_path, "w") as f:
                f.write(script_content)
            
            st = os.stat(update_script_path)
            os.chmod(update_script_path, st.st_mode | stat.S_IEXEC)
            
            subprocess.Popen([f"./{update_script_path}"], shell=False)
            sys.exit(0)
