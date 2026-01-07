import tkinter as tk
import sys
from PIL import Image, ImageTk

from utils import center_window
from backup import backup_database
from login_ui import LoginFrame

from inventory import open_inventory
from recipes import open_recipes
from make_cake import open_make_cake
from receipts_history import open_receipts_history
from reports import open_reports


# ---------- IMAGE HELPER ----------

def load_image(path, size):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


# ---------- DASHBOARD ----------

class DashboardFrame(tk.Frame):
    def __init__(self, master, role, on_logout):
        super().__init__(master, bg="#f2ebe3")
        self.on_logout = on_logout

        master.geometry("700x850")
        master.resizable(False, False)
        center_window(master, 700, 850)

        self.pack(fill="both", expand=True)

        header = tk.Frame(self, bg="#f2ebe3")
        header.pack(pady=20)

        logo = load_image("images/logo.png", (160, 160))
        self.logo_ref = logo

        tk.Label(header, image=logo, bg="#f2ebe3").pack()

        tk.Label(
            header,
            text="Bakery Management System",
            font=("Arial", 24, "bold"),
            bg="#f2ebe3",
            fg="#5a3b24"
        ).pack(pady=10)

        tk.Label(
            header,
            text=f"Dashboard | {role}",
            font=("Arial", 14),
            bg="#f2ebe3",
            fg="#7b5b3b"
        ).pack()

        grid = tk.Frame(self, bg="#f2ebe3")
        grid.pack(expand=True, pady=30)

        def dash_item(r, c, img, text, cmd):
            f = tk.Frame(grid, bg="#f2ebe3")
            f.grid(row=r, column=c, padx=60, pady=40)
            tk.Button(f, image=img, command=cmd, bd=0, bg="#f2ebe3").pack()
            tk.Label(f, text=text, font=("Arial", 12, "bold"),
                     bg="#f2ebe3").pack(pady=6)

        inventory = load_image("images/inventory.png", (128, 128))
        recipes = load_image("images/recipes.png", (128, 128))
        orders = load_image("images/orders.png", (128, 128))
        receipts = load_image("images/receipts.png", (128, 128))
        reports_img = load_image("images/reports.png", (128, 128))
        logout_img = load_image("images/exit.png", (128, 128))

        self.img_refs = [
            inventory, recipes, orders,
            receipts, reports_img, logout_img
        ]

        dash_item(0, 0, inventory, "Inventory", open_inventory)
        dash_item(0, 1, recipes, "Recipes", open_recipes)
        dash_item(0, 2, orders, "Make Cake", open_make_cake)
        dash_item(1, 0, receipts, "Receipts History", open_receipts_history)

        if role == "admin":
            dash_item(1, 1, reports_img, "Reports", open_reports)

        dash_item(1, 2, logout_img, "Logout", self.logout)

    def logout(self):
        self.destroy()
        show_login()   # no args


# ---------- APP CONTROLLER ----------

def show_login():
    LoginFrame(root, on_login=show_dashboard)


def show_dashboard(role):
    DashboardFrame(root, role, on_logout=show_login)


# ---------- ENTRY POINT ----------

if __name__ == "__main__":
    backup_database()

    root = tk.Tk()
    root.title("Bakery System")

    show_login()
    root.mainloop()

