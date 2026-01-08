import shutil
from datetime import datetime
from paths import get_db_path, get_backups_dir


LAST_BACKUP_FILE = "last_backup.txt"


def backup_database():
    db_path = get_db_path()
    backups_dir = get_backups_dir()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = f"{backups_dir}/bakery_{timestamp}.db"

    try:
        shutil.copy2(db_path, backup_path)

        # Save last backup time
        with open(LAST_BACKUP_FILE, "w") as f:
            f.write(datetime.now().isoformat())

        print(f"[BACKUP OK] {backup_path}")
        return backup_path

    except Exception as e:
        print(f"[BACKUP ERROR] {e}")
        return None
