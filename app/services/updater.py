import os
import sys
import platform
import requests
import threading
import subprocess
import shutil
import zipfile
import time
from pathlib import Path
from packaging import version
from app.core.version import VERSION

GITHUB_OWNER = "fleetimee"
GITHUB_REPO = "rbv-downloader-nov25"
API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

class Updater:
    def __init__(self):
        self.current_version = VERSION
        self.latest_version = None
        self.download_url = None
        self.release_url = None
        self.asset_name = self._get_asset_name()
        self.is_frozen = getattr(sys, 'frozen', False)

    def _get_asset_name(self):
        """
        Determine the correct asset name for the current OS/Arch.
        Matches the naming convention in .github/workflows/release.yml
        """
        system = platform.system()
        machine = platform.machine()
        
        if system == "Windows":
            return "RBV_Downloader-Windows-x64.exe"
        elif system == "Linux":
            return "RBV_Downloader-Linux-x64"
        elif system == "Darwin":
            if "arm64" in machine.lower():
                 return "RBV_Downloader-macOS-ARM64.zip"
            else:
                 return "RBV_Downloader-macOS-Intel.zip"
        return None

    def check_for_updates(self):
        """
        Checks GitHub for the latest release.
        Returns: (bool, str) -> (Update Available, New Version Tag)
        """
        try:
            response = requests.get(API_URL, timeout=5)
            if response.status_code != 200:
                print(f"[Updater] API check failed: {response.status_code}")
                return False, None
            
            data = response.json()
            tag_name = data.get("tag_name", "").strip()
            self.latest_version = tag_name.lstrip("v")
            self.release_url = data.get("html_url")
            
            if version.parse(self.latest_version) > version.parse(self.current_version):
                assets = data.get("assets", [])
                for asset in assets:
                    if asset["name"] == self.asset_name:
                        self.download_url = asset["browser_download_url"]
                        break
                
                if self.download_url:
                    return True, self.latest_version
                else:
                    print(f"[Updater] No matching asset found for {self.asset_name}")
            
        except Exception as e:
            print(f"[Updater] Error checking updates: {e}")
            
        return False, None

    def download_update(self, progress_callback=None):
        """
        Downloads the update file to a temporary path.
        progress_callback: function(current_bytes, total_bytes)
        Returns: path to downloaded file
        """
        if not self.download_url:
            return None
            
        try:
            response = requests.get(self.download_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            if self.is_frozen:
                 pass
            
            file_path = os.path.join(download_dir, self.asset_name)
            
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded_size, total_size)
                            
            return file_path
        except Exception as e:
            print(f"[Updater] Download failed: {e}")
            return None

    def install_update(self, file_path):
        """
        Handles the installation logic based on OS.
        Returns: (bool, message)
        """
        if not os.path.exists(file_path):
            return False, "Update file not found."
            
        system = platform.system()
        
        if system == "Darwin":
            try:
                extract_path = os.path.dirname(file_path)
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                
                subprocess.call(["open", "-R", file_path])
                return True, "Update downloaded to Downloads folder. Please replace the application."
            except Exception as e:
                return False, f"Failed to extract: {e}"

        elif system == "Windows":
            if not self.is_frozen:
                 return True, "Not running as frozen executable. Update saved to Downloads."

            current_exe = sys.executable
            new_exe = file_path
            batch_script = "update_installer.bat"
            
            script_content = f"""
@echo off
echo Waiting for application to close...
timeout /t 3 /nobreak > NUL
echo Updating...
move /y "{new_exe}" "{current_exe}"
echo Restarting...
start "" "{current_exe}"
del "%~f0"
"""
            try:
                with open(batch_script, "w") as f:
                    f.write(script_content)
                
                subprocess.Popen([batch_script], shell=True)
                return True, "restart_required"
            except Exception as e:
                return False, f"Failed to create installer: {e}"

        elif system == "Linux":
            if not self.is_frozen:
                 return True, "Not running as frozen executable. Update saved to Downloads."
            
            try:
                current_exe = sys.executable
                os.chmod(file_path, 0o755)
                
                shutil.move(current_exe, current_exe + ".old")
                shutil.move(file_path, current_exe)
                
                return True, "restart_required"
            except Exception as e:
                return False, f"Linux update failed: {e}"

        return False, "OS not supported for auto-install."

