import tkinter as tk
import os
import datetime
import shutil
from tkinter import messagebox
from PIL import Image, ImageTk

from utils import center_window
from login_ui import LoginFrame
from restore_backup import RestoreBackupWindow
from backup import backup_database
from backup_scheduler import SixHourBackupScheduler
from auto_logout import AutoLogoutManager

from inventory import open_inventory
from recipes import open_recipes
from make_cake import open_make_cake
from receipts_history import open_receipts_history
from reports import open_reports

from paths import is_frozen, get_db_path, get_bundle_path

def asset(path):
    """
    Return correct path for assets in dev and PyInstaller EXE
    """
    if is_frozen():
        return os.path.join(get_bundle_path(), path)
    return path



# ================== CONSTANTS ==================
LAST_BACKUP_FILE = "last_backup.txt"
BACKUP_INTERVAL_HOURS = 6

current_frame = None
backup_scheduler = None
auto_logout_manager = None


# ================== DATABASE INIT ==================
def ensure_database():
    if not is_frozen():
        return

    target_db = get_db_path()
    if os.path.exists(target_db):
        return

    bundled_db = os.path.join(get_bundle_path(), "bakery.db")
    if not os.path.exists(bundled_db):
        raise FileNotFoundError(bundled_db)

    os.makedirs(os.path.dirname(target_db), exist_ok=True)
    shutil.copy(bundled_db, target_db)


# ================== FRAME SWITCHER ==================
def switch_frame(frame_class, *args):
    global current_frame

    if current_frame is not None:
        current_frame.destroy()

    current_frame = frame_class(root, *args)
    print("FRAME CREATED:", type(current_frame))
    current_frame.pack(fill="both", expand=True)


# ================== BACKUP HELPERS ==================
def get_last_backup_datetime():
    if not os.path.exists(LAST_BACKUP_FILE):
        return None
    try:
        with open(LAST_BACKUP_FILE, "r") as f:
            return datetime.datetime.fromisoformat(f.read().strip())
    except Exception:
        return None


def get_last_backup_text():
    dt = get_last_backup_datetime()
    if not dt:
        return "Never"

    now = datetime.datetime.now()
    if dt.date() == now.date():
        return dt.strftime("%H:%M")

    return dt.strftime("%d/%m/%Y %H:%M")


def get_next_backup_due_text():
    dt = get_last_backup_datetime()
    if not dt:
        return "Now"

    next_due = dt + datetime.timedelta(hours=BACKUP_INTERVAL_HOURS)
    now = datetime.datetime.now()

    if now >= next_due:
        return "Now"

    remaining = next_due - now
    h = remaining.seconds // 3600
    m = (remaining.seconds % 3600) // 60
    return f"{h}h {m}m"


# ================== DASHBOARD ==================
class DashboardFrame(tk.Frame):
    def __init__(self, master, role):
        super().__init__(master, bg="#f2ebe3")
        global auto_logout_manager

        auto_logout_manager = AutoLogoutManager(
            root=master,
            timeout_minutes=5,
            on_timeout=self.logout
        )

        # ---------- HEADER ----------
        header = tk.Frame(self, bg="#f2ebe3")
        header.pack(pady=10)

        logo = ImageTk.PhotoImage(
            Image.open(asset("images/logo.png")).resize((120, 120))
        )
        self.logo_ref = logo

        tk.Label(header, image=logo, bg="#f2ebe3").pack()

        tk.Label(
            header,
            text="Bakery Management System",
            font=("Arial", 22, "bold"),
            bg="#f2ebe3",
            fg="#5a3b24"
        ).pack()

        tk.Label(
            header,
            text=f"Dashboard | {role}",
            font=("Arial", 13),
            bg="#f2ebe3",
            fg="#7b5b3b"
        ).pack()

        tk.Label(
            header,
            text=f"Last backup: {get_last_backup_text()}",
            font=("Arial", 10),
            bg="#f2ebe3"
        ).pack()

        tk.Label(
            header,
            text=f"Next backup due in: {get_next_backup_due_text()}",
            font=("Arial", 10),
            bg="#f2ebe3"
        ).pack()

        # ---------- GRID ----------
        grid = tk.Frame(self, bg="#f2ebe3")
        grid.pack(expand=True)

        for r in range(3):
            grid.rowconfigure(r, weight=1)
        for c in range(3):
            grid.columnconfigure(c, weight=1)

        def item(img, text, cmd, r, c):
            f = tk.Frame(grid, bg="#f2ebe3")
            f.grid(row=r, column=c, padx=30, pady=20)
            tk.Button(f, image=img, command=cmd, bd=0, bg="#f2ebe3").pack()
            tk.Label(f, text=text, bg="#f2ebe3").pack(pady=4)

        imgs = {
            "inv": ImageTk.PhotoImage(Image.open(asset("images/inventory.png")).resize((96, 96))),
            "rec": ImageTk.PhotoImage(Image.open(asset("images/recipes.png")).resize((96, 96))),
            "ord": ImageTk.PhotoImage(Image.open(asset("images/orders.png")).resize((96, 96))),
            "his": ImageTk.PhotoImage(Image.open(asset("images/receipts.png")).resize((96, 96))),
            "rep": ImageTk.PhotoImage(Image.open(asset("images/reports.png")).resize((96, 96))),
            "out": ImageTk.PhotoImage(Image.open(asset("images/exit.png")).resize((96, 96))),
            "bak": ImageTk.PhotoImage(Image.open(asset("images/backup.png")).resize((96, 96))),
            "res": ImageTk.PhotoImage(Image.open(asset("images/restore.png")).resize((96, 96))),
        }
        self.img_refs = imgs.values()

        # ---------- ROW 0 ----------
        item(imgs["inv"], "Inventory", open_inventory, 0, 0)
        item(imgs["rec"], "Recipes", open_recipes, 0, 1)
        item(imgs["ord"], "Make Cake", open_make_cake, 0, 2)

        # ---------- ROW 1 ----------
        item(imgs["his"], "Receipts History", open_receipts_history, 1, 0)

        if role == "admin":
            item(imgs["rep"], "Reports", open_reports, 1, 1)

        item(imgs["out"], "Logout", self.logout, 1, 2)

        # ---------- ROW 2 ----------
        if role == "admin":
            item(imgs["bak"], "Backup Now", self.manual_backup, 2, 0)
            item(
                imgs["res"],
                "Restore",
                lambda: RestoreBackupWindow(self.master),
                2,
                1
            )

    def manual_backup(self):
        backup_database()
        messagebox.showinfo(
            "Backup Complete",
            "Database backup created successfully."
        )

    def logout(self):
        global backup_scheduler, auto_logout_manager

        if auto_logout_manager:
            auto_logout_manager.stop()
            auto_logout_manager = None

        backup_scheduler = None
        show_login()


# ================== CONTROLLERS ==================
def show_login():
    root.geometry("360x260")
    center_window(root, 360, 260)
    switch_frame(LoginFrame, show_dashboard)


def show_dashboard(role):
    global backup_scheduler

    root.geometry("700x820")
    center_window(root, 700, 820)
    switch_frame(DashboardFrame, role)

    backup_scheduler = SixHourBackupScheduler(
        root=root,
        backup_func=backup_database,
        check_interval_minutes=10
    )


# ================== ENTRY POINT ==================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bakery System")

    ensure_database()
    show_login()

    root.mainloop()
