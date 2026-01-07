import tkinter as tk
from tkinter import messagebox

from auth import authenticate_user
from utils import center_window


def login_window(on_success):
    root = tk.Tk()
    root.title("Bakery Login")
    root.resizable(False, False)
    root.config(bg="#f2ebe3")

    center_window(root, 320, 220)

    # ---------- HEADER ----------
    tk.Label(
        root,
        text="Bakery Login",
        font=("Arial", 14, "bold"),
        bg="#f2ebe3",
        fg="#5a3b24"
    ).pack(pady=15)

    # ---------- FORM ----------
    form = tk.Frame(root, bg="#f2ebe3")
    form.pack(pady=5)

    tk.Label(form, text="Username", bg="#f2ebe3").grid(row=0, column=0, sticky="w")
    username_entry = tk.Entry(form, width=25)
    username_entry.grid(row=1, column=0, pady=5)

    tk.Label(form, text="Password", bg="#f2ebe3").grid(row=2, column=0, sticky="w")
    password_entry = tk.Entry(form, width=25, show="*")
    password_entry.grid(row=3, column=0, pady=5)

    # ---------- HELPERS ----------
    def reset_login_form():
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        username_entry.focus()

    # ---------- ACTION ----------
    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Info", "Please enter username and password")
            return

        user = authenticate_user(username, password)
        if user:
            reset_login_form()     # ✅ clear BEFORE hiding
            root.withdraw()
            on_success(user[0], root)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    tk.Button(
        root,
        text="Login",
        width=15,
        command=login,
        bg="#d9b382"
    ).pack(pady=15)

    reset_login_form()
    root.mainloop()

