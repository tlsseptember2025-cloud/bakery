import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from utils import center_window

def open_inventory():
    # --- Window setup ---
    win = tk.Toplevel()
    win.title("Inventory")
    center_window(win, 800, 500)
    #win.geometry("800x500")
    #win.minsize(700, 400)

    tk.Label(win, text="Current Inventory", font=("Arial", 14, "bold")).pack(pady=10)

    # --- Table frame ---
    table_frame = tk.Frame(win)
    table_frame.pack(fill="both", expand=True, padx=10)

    # --- Scrollbar ---
    tree_scroll = tk.Scrollbar(table_frame)
    tree_scroll.pack(side="right", fill="y")

    # --- Treeview table ---
    tree = ttk.Treeview(table_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
    tree.pack(fill="both", expand=True)
    tree_scroll.config(command=tree.yview)

    # --- Define columns ---
    tree['columns'] = ("Name", "Quantity", "Unit", "Alert Level")

    tree.column("#0", width=0, stretch=tk.NO)  # hide default column
    tree.column("Name", anchor=tk.W, width=200)
    tree.column("Quantity", anchor=tk.CENTER, width=100)
    tree.column("Unit", anchor=tk.CENTER, width=80)
    tree.column("Alert Level", anchor=tk.CENTER, width=100)

    # --- Create headings ---
    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("Name", text="Ingredient", anchor=tk.W)
    tree.heading("Quantity", text="Quantity", anchor=tk.CENTER)
    tree.heading("Unit", text="Unit", anchor=tk.CENTER)
    tree.heading("Alert Level", text="Alert Level", anchor=tk.CENTER)

    # --- Function to load inventory into table ---
    def load_inventory():
        for row in tree.get_children():  # clear table
            tree.delete(row)

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()
        cur.execute("SELECT name, quantity, unit, alert_level FROM ingredients")
        ingredients = cur.fetchall()
        conn.close()

        for item in ingredients:
            tree.insert("", tk.END, values=item)

    load_inventory()  # initial load

    # --- Add new ingredient form ---
    tk.Label(win, text="Add New Ingredient", font=("Arial", 12, "bold")).pack(pady=10)

    form_frame = tk.Frame(win)
    form_frame.pack(pady=5)

    tk.Label(form_frame, text="Name:").grid(row=0, column=0)
    tk.Label(form_frame, text="Quantity:").grid(row=1, column=0)
    tk.Label(form_frame, text="Unit:").grid(row=2, column=0)
    tk.Label(form_frame, text="Alert Level:").grid(row=3, column=0)

    name_entry = tk.Entry(form_frame)
    qty_entry = tk.Entry(form_frame)
    unit_entry = tk.Entry(form_frame)
    alert_entry = tk.Entry(form_frame)

    name_entry.grid(row=0, column=1)
    qty_entry.grid(row=1, column=1)
    unit_entry.grid(row=2, column=1)
    alert_entry.grid(row=3, column=1)

    # --- Add ingredient function with duplicate check ---
    def add_ingredient():
        try:
            name = name_entry.get().strip()
            qty = float(qty_entry.get())
            unit = unit_entry.get().strip()
            alert = float(alert_entry.get())

            conn = sqlite3.connect("bakery.db")
            cur = conn.cursor()

            # --- Check for duplicate ingredient (case-insensitive) ---
            cur.execute("SELECT * FROM ingredients WHERE LOWER(name)=?", (name.lower(),))
            existing = cur.fetchone()
            if existing:
                messagebox.showwarning("Duplicate Entry", f"'{name}' already exists in the inventory!")
                conn.close()
                return

            # --- Insert new ingredient ---
            cur.execute("INSERT INTO ingredients VALUES (NULL, ?, ?, ?, ?)", (name, qty, unit, alert))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"{name} added to inventory!")

            # Refresh table
            load_inventory()

            # Clear entries
            name_entry.delete(0, tk.END)
            qty_entry.delete(0, tk.END)
            unit_entry.delete(0, tk.END)
            alert_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add ingredient:\n{e}")

    tk.Button(win, text="Add Ingredient", command=add_ingredient, width=25).pack(pady=10)
