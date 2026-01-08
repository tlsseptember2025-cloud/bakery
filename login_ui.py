import tkinter as tk
from tkinter import messagebox

from auth import authenticate_user


class LoginFrame(tk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master, bg="#f2ebe3")
        self.on_login = on_login

        # ---------- UI ----------
        container = tk.Frame(self, bg="#f2ebe3")
        container.pack(expand=True)

        tk.Label(
            container,
            text="Bakery Login",
            font=("Arial", 18, "bold"),
            bg="#f2ebe3",
            fg="#5a3b24"
        ).pack(pady=20)

        form = tk.Frame(container, bg="#f2ebe3")
        form.pack()

        tk.Label(form, text="Username", bg="#f2ebe3").pack(anchor="w")
        self.username_entry = tk.Entry(form, width=28)
        self.username_entry.pack(pady=4)

        tk.Label(form, text="Password", bg="#f2ebe3").pack(anchor="w")
        self.password_entry = tk.Entry(form, width=28, show="*")
        self.password_entry.pack(pady=4)

        tk.Button(
            container,
            text="Login",
            width=18,
            bg="#d9b382",
            command=self.login
        ).pack(pady=18)

        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror(
                "Login Failed",
                "Please enter both username and password."
            )
            return

        user = authenticate_user(username, password)

        if user:
            role = user[0]
            self.on_login(role)   # main.py handles screen switch
        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )
