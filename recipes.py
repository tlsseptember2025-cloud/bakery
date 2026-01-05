import tkinter as tk
import sqlite3
from tkinter import messagebox
from utils import center_window

def open_recipes():
    win = tk.Toplevel()
    win.title("Recipes")
    center_window(win, 300, 200)
    win.geometry("300x200")

    tk.Label(win, text="Recipe Name").pack(pady=10)
    recipe_name = tk.Entry(win)
    recipe_name.pack()

    def add_recipe():
        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO recipes VALUES (NULL, ?)",
            (recipe_name.get(),)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Recipe added")

    tk.Button(win, text="Add Recipe", command=add_recipe).pack(pady=10)