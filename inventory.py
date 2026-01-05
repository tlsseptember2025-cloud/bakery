import tkinter as tk
import sqlite3
from tkinter import messagebox

def open_inventory():
    win = tk.Toplevel()
    win.title("Inventory")
    win.geometry("350x300")

    tk.Label(win, text="Ingredient Name").grid(row=0, column=0, padx=5, pady=5)
    tk.Label(win, text="Quantity").grid(row=1, column=0)
    tk.Label(win, text="Unit (ml/g)").grid(row=2, column=0)
    tk.Label(win, text="Alert Level").grid(row=3, column=0)

    name = tk.Entry(win)
    qty = tk.Entry(win)
    unit = tk.Entry(win)
    alert = tk.Entry(win)

    name.grid(row=0, column=1)
    qty.grid(row=1, column=1)
    unit.grid(row=2, column=1)
    alert.grid(row=3, column=1)

    def add_ingredient():
        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO ingredients VALUES (NULL, ?, ?, ?, ?)
        """, (
            name.get(),
            float(qty.get()),
            unit.get(),
            float(alert.get())
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Ingredient added")

    tk.Button(win, text="Add Ingredient", command=add_ingredient)\
        .grid(row=4, column=1, pady=10)