import os
import sys

def get_user_data_path(filename):
    """
    Returns a writable path for user data in the OS-specific app data directory.
    """
    if sys.platform == "win32":
        dir_path = os.path.join(os.environ['APPDATA'], "FlagGuessr")
    else:  # macOS, Linux
        base_dir = os.path.expanduser('~')
        if sys.platform == "darwin":
            # Correct path for macOS
            dir_path = os.path.join(base_dir, 'Library', 'Application Support', 'FlagGuessr')
        else:
            # Standard path for Linux
            dir_path = os.path.join(base_dir, '.local', 'share', 'FlagGuessr')
            
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, filename)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # When running from source, resolve resources from project root.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)
