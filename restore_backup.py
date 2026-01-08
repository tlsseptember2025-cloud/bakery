import os
import shutil
import tkinter as tk
from tkinter import messagebox

from utils import center_window
from paths import get_db_path, get_backups_dir


class RestoreBackupWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Restore Backup")
        self.resizable(False, False)
        center_window(self, 420, 360)
        self.configure(bg="#f2ebe3")

        self.transient(master)
        self.grab_set()

        tk.Label(
            self,
            text="Restore Database Backup",
            font=("Arial", 14, "bold"),
            bg="#f2ebe3",
            fg="#5a3b24"
        ).pack(pady=10)

        self.listbox = tk.Listbox(self, width=55, height=12)
        self.listbox.pack(pady=10)

        self.load_backups()

        btn_frame = tk.Frame(self, bg="#f2ebe3")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Restore Selected",
            width=18,
            bg="#c97b63",
            fg="white",
            command=self.restore_backup
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame,
            text="Cancel",
            width=18,
            command=self.destroy
        ).grid(row=0, column=1, padx=5)

    def load_backups(self):
        self.listbox.delete(0, tk.END)

        backups_dir = get_backups_dir()

        for file in sorted(os.listdir(backups_dir), reverse=True):
            if file.endswith(".db"):
                self.listbox.insert(tk.END, file)

    def restore_backup(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Select Backup",
                "Please select a backup file to restore."
            )
            return

        backup_file = self.listbox.get(selection[0])
        backup_path = os.path.join(get_backups_dir(), backup_file)

        confirm = messagebox.askyesno(
            "Confirm Restore",
            "This will overwrite the current database.\n\n"
            "Are you sure you want to continue?"
        )

        if confirm:
            try:
                shutil.copy2(backup_path, get_db_path())
                messagebox.showinfo(
                    "Restore Complete",
                    "Database restored successfully.\n\n"
                    "Please restart the application."
                )
                self.master.destroy()
            except Exception as e:
                messagebox.showerror(
                    "Restore Failed",
                    f"An error occurred:\n{e}"
                )

