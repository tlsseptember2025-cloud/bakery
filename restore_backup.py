import os
import shutil
import tkinter as tk
from tkinter import messagebox

DB_NAME = "bakery.db"
BACKUP_DIR = "backups"


class RestoreBackupWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Restore Backup")
        self.geometry("420x350")
        self.resizable(False, False)

        tk.Label(
            self,
            text="Restore Database Backup",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        self.listbox = tk.Listbox(self, width=55, height=12)
        self.listbox.pack(pady=10)

        self.load_backups()

        tk.Button(
            self,
            text="Restore Selected Backup",
            bg="#c97b63",
            fg="white",
            command=self.restore_backup
        ).pack(pady=10)

    def load_backups(self):
        self.listbox.delete(0, tk.END)

        if not os.path.isdir(BACKUP_DIR):
            return

        for file in sorted(os.listdir(BACKUP_DIR), reverse=True):
            if file.endswith(".db"):
                self.listbox.insert(tk.END, file)

    def restore_backup(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Select Backup", "Please select a backup file")
            return

        backup_file = self.listbox.get(selection[0])
        backup_path = os.path.join(BACKUP_DIR, backup_file)

        confirm = messagebox.askyesno(
            "Confirm Restore",
            "This will overwrite the current database.\n\nContinue?"
        )

        if confirm:
            shutil.copy2(backup_path, DB_NAME)
            messagebox.showinfo(
                "Restore Complete",
                "Database restored successfully.\n\nPlease restart the application."
            )
            self.master.destroy()
