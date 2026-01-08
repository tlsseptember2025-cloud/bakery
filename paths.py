import os
import sys

APP_NAME = "BakerySystem"


def is_frozen():
    return hasattr(sys, "_MEIPASS")


def get_bundle_path():
    if is_frozen():
        return sys._MEIPASS
    return os.path.abspath(".")


def get_app_data_dir():
    path = os.path.join(os.getenv("APPDATA"), APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def get_db_path():
    if is_frozen():
        return os.path.join(get_app_data_dir(), "bakery.db")
    return os.path.join(get_bundle_path(), "bakery.db")


def get_backups_dir():
    """
    Canonical backups directory (same for backup & restore)
    """
    if is_frozen():
        base = get_app_data_dir()
    else:
        base = get_bundle_path()

    path = os.path.join(base, "backups")
    os.makedirs(path, exist_ok=True)
    return path
