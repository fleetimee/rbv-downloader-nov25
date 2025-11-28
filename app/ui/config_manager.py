import os
import json

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".rbv_downloader_config.json")

class ConfigManager:
    @staticmethod
    def load_config():
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", "RBV-Downloader")
        defaults = {
            "module_code": "", 
            "phpsessid": "", 
            "sucuri_cookie": "",
            "download_path": default_path,
            "check_updates_on_startup": False
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    defaults.update(loaded)
                    return defaults
            except:
                pass
        return defaults

    @staticmethod
    def save_config(data):
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
