import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from utils import center_window

def open_inventory():
    win = tk.Toplevel()
    win.title("Inventory")
    center_window(win, 800, 500)

    # Bring window to front and focus initially
    win.lift()
    win.focus_force()

    tk.Label(win, text="Current Inventory", font=("Arial", 14, "bold")).pack(pady=10)

    # ---Table frame---
    table_frame = tk.Frame(win)
    table_frame.pack(fill="both", expand=True, padx=10)

    tree_scroll = tk.Scrollbar(table_frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(table_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
    tree.pack(fill="both", expand=True)
    tree_scroll.config(command=tree.yview)

    tree['columns'] = ("Name", "Quantity", "Unit", "Alert Level")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("Name", anchor=tk.W, width=200)
    tree.column("Quantity", anchor=tk.CENTER, width=100)
    tree.column("Unit", anchor=tk.CENTER, width=80)
    tree.column("Alert Level", anchor=tk.CENTER, width=100)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("Name", text="Ingredient", anchor=tk.W)
    tree.heading("Quantity", text="Quantity", anchor=tk.CENTER)
    tree.heading("Unit", text="Unit", anchor=tk.CENTER)
    tree.heading("Alert Level", text="Alert Level", anchor=tk.CENTER)

    # --- Load inventory ---
    def load_inventory():
        for row in tree.get_children():
            tree.delete(row)

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()
        cur.execute("SELECT name, quantity, unit, alert_level FROM ingredients")
        ingredients = cur.fetchall()
        conn.close()

        for item in ingredients:
            row_id = tree.insert("", tk.END, values=item)
            if item[1] <= item[3]:  # Highlight low stock
                tree.item(row_id, tags=('low_stock',))
        tree.tag_configure('low_stock', background='pink')

    load_inventory()

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

    # --- Add Ingredient function ---
    def add_ingredient():
        try:
            name = name_entry.get().strip()
            qty = float(qty_entry.get())
            unit = unit_entry.get().strip()
            alert = float(alert_entry.get())

            conn = sqlite3.connect("bakery.db")
            cur = conn.cursor()

            cur.execute("SELECT * FROM ingredients WHERE LOWER(name)=?", (name.lower(),))
            if cur.fetchone():
                messagebox.showwarning("Duplicate Entry", f"'{name}' already exists!", parent=win)
                conn.close()
                win.lift()
                win.focus_force()
                return

            cur.execute("INSERT INTO ingredients VALUES (NULL, ?, ?, ?, ?)", (name, qty, unit, alert))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"{name} added to inventory!", parent=win)

            load_inventory()
            win.lift()
            win.focus_force()

            # Clear input fields
            name_entry.delete(0, tk.END)
            qty_entry.delete(0, tk.END)
            unit_entry.delete(0, tk.END)
            alert_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add ingredient:\n{e}", parent=win)
            win.lift()
            win.focus_force()

    tk.Button(win, text="Add Ingredient", command=add_ingredient, width=25).pack(pady=5)

    # --- Restock selected item ---
    def restock_item():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an ingredient to restock.", parent=win)
            win.lift()
            win.focus_force()
            return

        item = tree.item(selected)
        name = item['values'][0]

        restock_win = tk.Toplevel()
        restock_win.title(f"Restock {name}")
        center_window(restock_win, 300, 150)

        tk.Label(restock_win, text=f"Add quantity for {name}:").pack(pady=10)
        qty_entry = tk.Entry(restock_win)
        qty_entry.pack(pady=5)

        def confirm_restock():
            try:
                add_qty = float(qty_entry.get())
                if add_qty <= 0:
                    messagebox.showerror("Error", "Please enter a positive number.", parent=restock_win)
                    win.lift()
                    win.focus_force()
                    return

                conn = sqlite3.connect("bakery.db")
                cur = conn.cursor()
                cur.execute("UPDATE ingredients SET quantity = quantity + ? WHERE name=?", (add_qty, name))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"{add_qty} added to {name}!", parent=win)
                load_inventory()
                win.lift()
                win.focus_force()
                restock_win.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to restock:\n{e}", parent=restock_win)
                win.lift()
                win.focus_force()

        tk.Button(restock_win, text="Add Quantity", command=confirm_restock).pack(pady=10)

    tk.Button(win, text="Restock Selected Item", command=restock_item, width=25).pack(pady=10)

    # --- Close Inventory Button ---
    tk.Button(win, text="Close Inventory", command=win.destroy, width=25, bg="lightcoral").pack(pady=10)



