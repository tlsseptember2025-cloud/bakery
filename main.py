import tkinter as tk
import os
import datetime
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


import os
import shutil
from paths import is_frozen, get_db_path

if is_frozen():
    db_target = get_db_path()
    if not os.path.exists(db_target):
        shutil.copy("bakery.db", db_target)


LAST_BACKUP_FILE = "last_backup.txt"
BACKUP_INTERVAL_HOURS = 6

auto_logout_manager = None
backup_scheduler = None


# ---------- HELPERS ----------

def load_image(path, size):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def format_datetime_ddmmyyyy_hhmm(dt):
    return dt.strftime("%d/%m/%Y %H:%M")


def format_time_hhmm(dt):
    return dt.strftime("%H:%M")


def get_last_backup_datetime():
    if not os.path.exists(LAST_BACKUP_FILE):
        return None

    try:
        with open(LAST_BACKUP_FILE, "r") as f:
            raw = f.read().strip()

        if "T" in raw:
            return datetime.datetime.fromisoformat(raw)
        else:
            return datetime.datetime.combine(
                datetime.date.fromisoformat(raw),
                datetime.datetime.min.time()
            )
    except Exception:
        return None


def get_last_backup_text():
    last_dt = get_last_backup_datetime()
    if not last_dt:
        return "Never"

    now = datetime.datetime.now()
    today = now.date()

    if last_dt.date() == today:
        # ✅ Today → show time only
        return format_time_hhmm(last_dt)
    else:
        # ✅ Older → show full date + time
        return format_datetime_ddmmyyyy_hhmm(last_dt)


def get_next_backup_due_text():
    last_dt = get_last_backup_datetime()
    if not last_dt:
        return "Now"

    next_due = last_dt + datetime.timedelta(hours=BACKUP_INTERVAL_HOURS)
    now = datetime.datetime.now()

    if now >= next_due:
        return "Now"

    remaining = next_due - now
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60

    return f"{hours}h {minutes}m"


# ---------- DASHBOARD ----------

class DashboardFrame(tk.Frame):
    def __init__(self, master, role):
        super().__init__(master, bg="#f2ebe3")
        global auto_logout_manager

        master.geometry("700x820")
        master.resizable(False, False)
        center_window(master, 700, 820)

        self.pack(fill="both", expand=True)

        # ⏱️ AUTO LOGOUT (5 MIN)
        auto_logout_manager = AutoLogoutManager(
            root=master,
            timeout_minutes=5,
            on_timeout=self.logout
        )

        # ---------- HEADER ----------
        header = tk.Frame(self, bg="#f2ebe3")
        header.pack(pady=8)

        logo = load_image("images/logo.png", (120, 120))
        self.logo_ref = logo

        tk.Label(header, image=logo, bg="#f2ebe3").pack()

        tk.Label(
            header,
            text="Bakery Management System",
            font=("Arial", 22, "bold"),
            bg="#f2ebe3",
            fg="#5a3b24"
        ).pack(pady=4)

        tk.Label(
            header,
            text=f"Dashboard | {role}",
            font=("Arial", 13),
            bg="#f2ebe3",
            fg="#7b5b3b"
        ).pack()

        self.last_backup_label = tk.Label(
            header,
            text=f"Last backup: {get_last_backup_text()}",
            font=("Arial", 10),
            bg="#f2ebe3",
            fg="#6b5a4a"
        )
        self.last_backup_label.pack(pady=1)

        self.next_backup_label = tk.Label(
            header,
            text=f"Next backup due in: {get_next_backup_due_text()}",
            font=("Arial", 10),
            bg="#f2ebe3",
            fg="#6b5a4a"
        )
        self.next_backup_label.pack(pady=1)

        self.update_backup_labels()

        # ---------- GRID ----------
        grid = tk.Frame(self, bg="#f2ebe3")
        grid.pack(expand=True)

        for r in range(3):
            grid.rowconfigure(r, weight=1)
        for c in range(3):
            grid.columnconfigure(c, weight=1)

        def dash_item(row, col, img, text, cmd):
            frame = tk.Frame(grid, bg="#f2ebe3")
            frame.grid(row=row, column=col, padx=35, pady=20)

            tk.Button(
                frame,
                image=img,
                command=cmd,
                bd=0,
                bg="#f2ebe3",
                activebackground="#f2ebe3"
            ).pack()

            tk.Label(
                frame,
                text=text,
                font=("Arial", 11, "bold"),
                bg="#f2ebe3",
                fg="#3b2a1a"
            ).pack(pady=4)

        inventory = load_image("images/inventory.png", (96, 96))
        recipes = load_image("images/recipes.png", (96, 96))
        orders = load_image("images/orders.png", (96, 96))
        receipts = load_image("images/receipts.png", (96, 96))
        reports_img = load_image("images/reports.png", (96, 96))
        logout_img = load_image("images/exit.png", (96, 96))
        backup_img = load_image("images/backup.png", (96, 96))
        restore_img = load_image("images/restore.png", (96, 96))

        self.img_refs = [
            inventory, recipes, orders,
            receipts, reports_img,
            logout_img, backup_img, restore_img
        ]

        dash_item(0, 0, inventory, "Inventory", open_inventory)
        dash_item(0, 1, recipes, "Recipes", open_recipes)
        dash_item(0, 2, orders, "Make Cake", open_make_cake)

        dash_item(1, 0, receipts, "Receipts History", open_receipts_history)

        if role == "admin":
            dash_item(1, 1, reports_img, "Reports", open_reports)

        dash_item(1, 2, logout_img, "Logout", self.logout)

        if role == "admin":
            dash_item(2, 0, backup_img, "Backup Now", self.manual_backup)
            dash_item(
                2, 1,
                restore_img,
                "Restore",
                lambda: RestoreBackupWindow(self.master)
            )

    # ---------- BACKUP LABEL REFRESH ----------

    def update_backup_labels(self):
        self.last_backup_label.config(
            text=f"Last backup: {get_last_backup_text()}"
        )
        self.next_backup_label.config(
            text=f"Next backup due in: {get_next_backup_due_text()}"
        )
        self.after(60_000, self.update_backup_labels)

    # ---------- ACTIONS ----------

    def manual_backup(self):
        backup_database()
        self.update_backup_labels()
        messagebox.showinfo(
            "Backup Complete",
            "Database backup created successfully."
        )

    def logout(self):
        global auto_logout_manager, backup_scheduler

        if auto_logout_manager:
            auto_logout_manager.stop()
            auto_logout_manager = None

        backup_scheduler = None
        self.destroy()
        show_login()


# ---------- CONTROLLER ----------

def show_login():
    LoginFrame(root, show_dashboard)


def show_dashboard(role):
    global backup_scheduler

    DashboardFrame(root, role)

    # 🔄 Start backup checks AFTER login
    backup_scheduler = SixHourBackupScheduler(
        root=root,
        backup_func=backup_database,
        check_interval_minutes=10
    )


# ---------- ENTRY POINT ----------

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bakery System")

    show_login()
    root.mainloop()

