import os
import shutil
from datetime import datetime

DB_NAME = "bakery.db"
BACKUP_DIR = "backups"
LAST_BACKUP_FILE = "last_backup.txt"


def backup_database():
    if not os.path.isfile(DB_NAME):
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(BACKUP_DIR, f"bakery_{timestamp}.db")

    try:
        shutil.copy2(DB_NAME, backup_path)

        # ✅ Update last backup timestamp
        with open(LAST_BACKUP_FILE, "w") as f:
            f.write(datetime.now().isoformat())

        print(f"[BACKUP OK] {backup_path}")
    except Exception as e:
        print(f"[BACKUP ERROR] {e}")
