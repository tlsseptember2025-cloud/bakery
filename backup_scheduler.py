import os
import datetime
from tkinter import messagebox

LAST_BACKUP_FILE = "last_backup.txt"
BACKUP_INTERVAL_HOURS = 6


class SixHourBackupScheduler:
    """
    Backup every 6 hours.
    Popup NEVER blocks app startup.
    """

    def __init__(self, root, backup_func, check_interval_minutes=10):
        self.root = root
        self.backup_func = backup_func
        self.check_interval_ms = check_interval_minutes * 60 * 1000

        # 🔑 Delay first check so UI can load
        self.root.after(1000, self.check_and_backup)
        self.schedule_next_check()

    # ---------- TIME HELPERS ----------

    def get_last_backup_time(self):
        if not os.path.exists(LAST_BACKUP_FILE):
            return None

        try:
            with open(LAST_BACKUP_FILE, "r") as f:
                raw = f.read().strip()

            # New format (datetime)
            if "T" in raw:
                return datetime.datetime.fromisoformat(raw)

            # Old format (date only) → upgrade safely
            date_only = datetime.date.fromisoformat(raw)
            upgraded = datetime.datetime.combine(
                date_only,
                datetime.datetime.now().time()
            )
            self.set_last_backup_time(upgraded)
            return upgraded

        except Exception:
            return None

    def set_last_backup_time(self, dt):
        try:
            with open(LAST_BACKUP_FILE, "w") as f:
                f.write(dt.isoformat())
        except Exception:
            pass

    # ---------- CORE LOGIC ----------

    def check_and_backup(self):
        now = datetime.datetime.now()
        last_backup = self.get_last_backup_time()

        if not last_backup:
            self.prompt_backup()
            return

        hours_passed = (now - last_backup).total_seconds() / 3600

        if hours_passed >= BACKUP_INTERVAL_HOURS:
            self.prompt_backup()

    def prompt_backup(self):
        # 🔑 Run popup AFTER Tk is idle (non-blocking startup)
        self.root.after(0, self._show_popup)

    def _show_popup(self):
        answer = messagebox.askyesno(
            "Backup Required",
            "It has been more than 6 hours since the last backup.\n\n"
            "Would you like to create a backup now?"
        )

        if answer:
            self.backup_func()
            self.set_last_backup_time(datetime.datetime.now())
        # ❌ If NO → do nothing (retry later automatically)

    # ---------- SCHEDULING ----------

    def schedule_next_check(self):
        self.root.after(self.check_interval_ms, self.run)

    def run(self):
        self.check_and_backup()
        self.schedule_next_check()

