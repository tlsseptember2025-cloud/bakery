import os
import shutil
from datetime import datetime

DB_NAME = "bakery.db"
BACKUP_DIR = "backups"


def backup_database():
    """
    Create a timestamped backup of the SQLite database.
    Safe to call multiple times.
    """
    # If database does not exist, do nothing
    if not os.path.isfile(DB_NAME):
        return

    # Create backups folder if it doesn't exist
    if not os.path.isdir(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # Timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"bakery_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        # copy2 preserves file metadata
        shutil.copy2(DB_NAME, backup_path)
        print(f"[BACKUP] Database backed up to {backup_path}")
    except Exception as e:
        print(f"[BACKUP ERROR] {e}")

