import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def open_folder(path):
    if not path:
        path = os.path.abspath("downloads")

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            pass
    
    if os.name == 'nt':
        os.startfile(path)
    elif os.name == 'posix':
        os.system(f'open "{path}"' if sys.platform == 'darwin' else f'xdg-open "{path}"')
