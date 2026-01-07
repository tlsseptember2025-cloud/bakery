import tkinter as tk
import sys
from PIL import Image, ImageTk

from utils import center_window
from inventory import open_inventory
from recipes import open_recipes
from make_cake import open_make_cake
from receipts_history import open_receipts_history
from reports import open_reports
from login_ui import login_window


# --------- IMAGE HELPER ---------

def load_image(path, size):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


# --------- APP CONTROL ---------

def logout(dashboard, login_root):
    """Close dashboard and return to login screen"""
    if dashboard.winfo_exists():
        dashboard.destroy()
    login_root.deiconify()


def exit_app(login_root):
    """Completely terminate the application"""
    try:
        login_root.quit()
        login_root.destroy()
    finally:
        sys.exit(0)


# --------- DASHBOARD ---------

def start_app(role, login_root):
    dashboard = tk.Toplevel(login_root)
    dashboard.title("Bakery Shop")

    # ✅ FIX: Close button (❌) behaves like Logout
    dashboard.protocol(
        "WM_DELETE_WINDOW",
        lambda: logout(dashboard, login_root)
    )

    center_window(dashboard, 700, 850)
    dashboard.config(bg="#f2ebe3")

    # ---------- LOAD IMAGES ----------
    logo_img = load_image("images/logo.png", (180, 180))
    inventory_img = load_image("images/inventory.png", (128, 128))
    recipes_img = load_image("images/recipes.png", (128, 128))
    orders_img = load_image("images/orders.png", (128, 128))
    receipts_img = load_image("images/receipts.png", (128, 128))
    reports_img = load_image("images/reports.png", (128, 128))
    exit_img = load_image("images/exit.png", (128, 128))

    dashboard.image_refs = [
        logo_img, inventory_img, recipes_img,
        orders_img, receipts_img, reports_img, exit_img
    ]

    # ---------- HEADER ----------
    header = tk.Frame(dashboard, bg="#f2ebe3")
    header.pack(pady=20)

    tk.Label(header, image=logo_img, bg="#f2ebe3").pack()

    tk.Label(
        header,
        text="Bakery Management System",
        font=("Arial", 24, "bold"),
        bg="#f2ebe3",
        fg="#5a3b24"
    ).pack(pady=10)

    tk.Label(
        header,
        text=f"Dashboard | Logged in as: {role}",
        font=("Arial", 14),
        bg="#f2ebe3",
        fg="#7b5b3b"
    ).pack()

    # ---------- DASHBOARD GRID ----------
    dashboard_frame = tk.Frame(dashboard, bg="#f2ebe3")
    dashboard_frame.pack(expand=True, pady=30)

    def dash_item(row, col, img, text, cmd):
        frame = tk.Frame(dashboard_frame, bg="#f2ebe3")
        frame.grid(row=row, column=col, padx=60, pady=40)

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
            font=("Arial", 12, "bold"),
            bg="#f2ebe3",
            fg="#3b2a1a"
        ).pack(pady=6)

    # ---------- BUTTONS ----------
    dash_item(0, 0, inventory_img, "Inventory", open_inventory)
    dash_item(0, 1, recipes_img, "Recipes", open_recipes)
    dash_item(0, 2, orders_img, "Make Cake", open_make_cake)

    dash_item(1, 0, receipts_img, "Receipts History", open_receipts_history)

    if role == "admin":
        dash_item(1, 1, reports_img, "Reports", open_reports)

    dash_item(1, 2, exit_img, "Logout", lambda: logout(dashboard, login_root))
    dash_item(2, 2, exit_img, "Exit", lambda: exit_app(login_root))

    # ---------- FOOTER ----------
    tk.Label(
        dashboard,
        text="© 2026 My Bakery | Splash Dashboard",
        font=("Arial", 9),
        bg="#f2ebe3",
        fg="#8c6b4a"
    ).pack(pady=5)


# --------- APP ENTRY POINT ---------

if __name__ == "__main__":
    login_window(start_app)

