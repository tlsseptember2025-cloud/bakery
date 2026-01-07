import tkinter as tk
from tkinter import messagebox

from auth import authenticate_user
from utils import center_window


class LoginFrame(tk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master, bg="#f2ebe3")
        self.on_login = on_login

        master.geometry("360x260")
        master.resizable(False, False)
        center_window(master, 360, 260)

        self.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self,
            text="Bakery Login",
            font=("Arial", 18, "bold"),
            bg="#f2ebe3",
            fg="#5a3b24"
        ).pack(pady=20)

        form = tk.Frame(self, bg="#f2ebe3")
        form.pack()

        tk.Label(form, text="Username", bg="#f2ebe3").pack(anchor="w")
        self.username = tk.Entry(form, width=28)
        self.username.pack(pady=4)

        tk.Label(form, text="Password", bg="#f2ebe3").pack(anchor="w")
        self.password = tk.Entry(form, width=28, show="*")
        self.password.pack(pady=4)

        tk.Button(
            self,
            text="Login",
            width=18,
            bg="#d9b382",
            command=self.login
        ).pack(pady=18)

        self.username.focus()

    def login(self):
        user = authenticate_user(
            self.username.get().strip(),
            self.password.get().strip()
        )

        if user:
            self.destroy()
            self.on_login(user[0])   # role
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

