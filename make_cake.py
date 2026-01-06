import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime
from utils import center_window


def ensure_receipts_table():
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS receipts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT,
            quantity INTEGER,
            customer_name TEXT,
            total REAL,
            receipt_text TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_receipt(recipe_name, qty, customer, total, receipt_text):
    ensure_receipts_table()

    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO receipts(recipe_name, quantity, customer_name, total, receipt_text, created_at)
        VALUES(?,?,?,?,?,?)
        """,
        (
            recipe_name,
            qty,
            customer,
            total,
            receipt_text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()
    conn.close()


def open_make_cake():
    win = tk.Toplevel()
    win.title("Make Cake")
    center_window(win, 650, 520)

    win.lift()
    win.focus_force()

    tk.Label(win, text="Make Cake", font=("Arial", 16, "bold")).pack(pady=10)

    tk.Label(win, text="Select Recipe").pack()
    recipe_combo = ttk.Combobox(win, width=35, state="readonly")
    recipe_combo.pack(pady=5)

    tk.Label(win, text="Quantity").pack()
    qty_entry = tk.Entry(win, width=20)
    qty_entry.pack(pady=5)

    tk.Label(win, text="Customer Name (optional)").pack()
    cust_entry = tk.Entry(win, width=35)
    cust_entry.pack(pady=5)

    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM recipes ORDER BY name")
    recipes = cur.fetchall()
    conn.close()

    recipe_map = {name: rid for rid, name in recipes}
    recipe_combo["values"] = list(recipe_map.keys())

    def make():
        recipe = recipe_combo.get()
        qty = qty_entry.get()
        customer = cust_entry.get().strip()

        if not recipe or not qty:
            messagebox.showerror("Error", "Select recipe and enter qty", parent=win)
            return

        try:
            qty = int(qty)
            if qty <= 0:
                raise Exception
        except:
            messagebox.showerror("Error", "Qty must be positive number", parent=win)
            return

        recipe_id = recipe_map[recipe]

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()

        cur.execute("SELECT selling_price FROM recipes WHERE id=?", (recipe_id,))
        price = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT ri.quantity, i.quantity, i.id
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,))

        rows = cur.fetchall()

        # Check stock
        for req, avail, _ in rows:
            if avail < (req * qty):
                messagebox.showerror("Low Stock", "Not enough ingredients")
                conn.close()
                return

        # Deduct stock
        for req, avail, ing_id in rows:
            new = avail - (req * qty)
            cur.execute("UPDATE ingredients SET quantity=? WHERE id=?", (new, ing_id))

        conn.commit()
        conn.close()

        total = price * qty

        # -------- Receipt Text --------
        os.makedirs("receipts", exist_ok=True)
        path = f"receipts/{recipe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        txt = f"""
BAKERY RECEIPT
===========================
Customer : {customer if customer else "N/A"}
Recipe   : {recipe}
Quantity : {qty}

Price per Cake : {price:.2f}
Total Amount   : {total:.2f}

Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(path, "w") as f:
            f.write(txt)

        save_receipt(recipe, qty, customer, total, txt)

        messagebox.showinfo("Success", f"Cake Made!\nReceipt Saved:\n{path}", parent=win)

    tk.Button(win, text="Make Cake", command=make, width=20).pack(pady=20)
