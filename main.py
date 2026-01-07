import tkinter as tk
import sys
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


LAST_BACKUP_FILE = "last_backup.txt"


# ---------- HELPERS ----------

def load_image(path, size):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def format_date_ddmmyyyy(date_obj):
    return date_obj.strftime("%d/%m/%Y")


def get_last_backup_text():
    if not os.path.exists(LAST_BACKUP_FILE):
        return "Never"

    try:
        with open(LAST_BACKUP_FILE, "r") as f:
            raw = f.read().strip()

        # Handle datetime OR date-only
        if "T" in raw:
            last_dt = datetime.datetime.fromisoformat(raw)
            last_date = last_dt.date()
        else:
            last_date = datetime.date.fromisoformat(raw)

    except Exception:
        return "Unknown"

    today = datetime.date.today()

    if last_date == today:
        return "Today"
    elif last_date == today - datetime.timedelta(days=1):
        return "Yesterday"
    else:
        return format_date_ddmmyyyy(last_date)


auto_logout_manager = None


# ---------- DASHBOARD ----------

class DashboardFrame(tk.Frame):
    def __init__(self, master, role):
        super().__init__(master, bg="#f2ebe3")
        global auto_logout_manager

        master.geometry("700x820")
        master.resizable(False, False)
        center_window(master, 700, 820)

        self.pack(fill="both", expand=True)

        # ⏱️ AUTO LOGOUT (5 MINUTES)
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

        # ✅ LAST BACKUP LABEL
        self.backup_label = tk.Label(
            header,
            text=f"Last backup: {get_last_backup_text()}",
            font=("Arial", 10),
            bg="#f2ebe3",
            fg="#6b5a4a"
        )
        self.backup_label.pack(pady=2)

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

        # ---------- ICONS ----------
        inventory = load_image("images/inventory.png", (96, 96))
        recipes = load_image("images/recipes.png", (96, 96))
        orders = load_image("images/orders.png", (96, 96))
        receipts = load_image("images/receipts.png", (96, 96))
        reports_img = load_image("images/reports.png", (96, 96))
        logout_img = load_image("images/exit.png", (96, 96))
        backup_img = load_image("images/restore.png", (96, 96))
        restore_img = load_image("images/restore.png", (96, 96))

        self.img_refs = [
            inventory, recipes, orders,
            receipts, reports_img,
            logout_img, backup_img, restore_img
        ]

        # ---------- ROW 0 ----------
        dash_item(0, 0, inventory, "Inventory", open_inventory)
        dash_item(0, 1, recipes, "Recipes", open_recipes)
        dash_item(0, 2, orders, "Make Cake", open_make_cake)

        # ---------- ROW 1 ----------
        dash_item(1, 0, receipts, "Receipts History", open_receipts_history)

        if role == "admin":
            dash_item(1, 1, reports_img, "Reports", open_reports)

        dash_item(1, 2, logout_img, "Logout", self.logout)

        # ---------- ROW 2 (ADMIN ONLY) ----------
        if role == "admin":
            dash_item(2, 0, backup_img, "Backup Now", self.manual_backup)
            dash_item(2, 1,restore_img,"Restore Backup",lambda: RestoreBackupWindow(self.master))

    # ---------- ACTIONS ----------

    def manual_backup(self):
        backup_database()
        self.backup_label.config(
            text=f"Last backup: {get_last_backup_text()}"
        )
        messagebox.showinfo(
            "Backup Complete",
            "Database backup created successfully."
        )

    def logout(self):
        global auto_logout_manager

        if auto_logout_manager:
            auto_logout_manager.stop()
            auto_logout_manager = None

        self.destroy()
        show_login()


# ---------- CONTROLLER ----------

def show_login():
    LoginFrame(root, show_dashboard)


def show_dashboard(role):
    DashboardFrame(root, role)


# ---------- ENTRY POINT ----------

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bakery System")

    # 🔄 Backup every 6 hours (with missed-backup popup)
    backup_scheduler = SixHourBackupScheduler(
        root=root,
        backup_func=backup_database,
        check_interval_minutes=10
    )

    show_login()
    root.mainloop()
