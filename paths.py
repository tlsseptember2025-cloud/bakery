import os
import sys

APP_NAME = "BakerySystem"

def is_frozen():
    return hasattr(sys, "_MEIPASS")

def get_app_data_dir():
    path = os.path.join(os.getenv("APPDATA"), APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path

def get_db_path():
    if is_frozen():
        return os.path.join(get_app_data_dir(), "bakery.db")
    return "bakery.db"
