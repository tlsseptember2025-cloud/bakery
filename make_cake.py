import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime
from utils import center_window


# ================= HELPERS =================

def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0


def ensure_receipts_table():
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT,
            receipt_text TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_receipt_to_db(recipe_name, receipt_text):
    ensure_receipts_table()

    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO receipts (recipe_name, receipt_text, created_at)
        VALUES (?, ?, ?)
    """, (
        recipe_name,
        receipt_text,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def ensure_cost_column():
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(ingredients)")
    cols = [row[1].lower() for row in cur.fetchall()]
    if "cost_per_unit" not in cols:
        cur.execute("ALTER TABLE ingredients ADD COLUMN cost_per_unit REAL DEFAULT 0")
        conn.commit()
    conn.close()


def generate_receipt(recipe_name, ingredients):
    """
    ingredients: list of tuples (name, qty, unit, cost_per_unit)
    """
    os.makedirs("receipts", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"receipts/{recipe_name}_{timestamp}.txt"

    lines = [
        "BAKERY RECEIPT",
        "=" * 35,
        f"Recipe: {recipe_name}",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Ingredients Used:"
    ]

    total_cost = 0.0

    for name, qty, unit, cost_per_unit in ingredients:
        qty = safe_float(qty)
        cpu = safe_float(cost_per_unit)
        line_cost = qty * cpu
        total_cost += line_cost
        if cpu > 0:
            lines.append(f"- {name}: {qty} {unit} (cost: {line_cost:.2f})")
        else:
            lines.append(f"- {name}: {qty} {unit}")

    lines.append("")
    lines.append(f"Estimated Total Cost: {total_cost:.2f}")
    lines.append("")
    lines.append("Thank you!")

    receipt_text = "\n".join(lines)

    # save to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(receipt_text)

    # save to DB
    save_receipt_to_db(recipe_name, receipt_text)

    return file_path, receipt_text


def show_receipt_preview(parent, receipt_text, file_path):
    preview = tk.Toplevel(parent)
    preview.title("Receipt Preview")
    center_window(preview, 500, 500)

    preview.transient(parent)
    preview.grab_set()
    preview.lift()
    preview.attributes("-topmost", True)
    preview.after(150, lambda: preview.attributes("-topmost", False))
    preview.focus_force()

    tk.Label(preview, text="Receipt Preview", font=("Arial", 14, "bold")).pack(pady=10)

    text_box = tk.Text(
        preview,
        font=("Courier New", 11),
        wrap="word",
        bg="#f9f9f9"
    )
    text_box.pack(fill="both", expand=True, padx=10, pady=10)
    text_box.insert("1.0", receipt_text)
    text_box.config(state="disabled")

    tk.Label(
        preview,
        text=f"Saved to file: {file_path}",
        font=("Arial", 9)
    ).pack(pady=5)

    tk.Button(preview, text="Close", width=15, command=preview.destroy).pack(pady=10)

    preview.wait_window()


# ================= MAIN WINDOW =================

def open_make_cake():
    ensure_cost_column()  # make sure cost_per_unit exists

    win = tk.Toplevel()
    win.title("Make Cake")
    center_window(win, 600, 450)
    win.lift()
    win.focus_force()

    tk.Label(win, text="Make Cake", font=("Arial", 16, "bold")).pack(pady=15)

    tk.Label(win, text="Select Recipe", font=("Arial", 12)).pack()
    recipe_combo = ttk.Combobox(win, state="readonly", width=35)
    recipe_combo.pack(pady=10)

    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM recipes ORDER BY name ASC")
    recipes = cur.fetchall()
    conn.close()

    recipe_map = {name: rid for rid, name in recipes}
    recipe_combo["values"] = list(recipe_map.keys())

    def make_cake():
        recipe_name = recipe_combo.get()
        if not recipe_name:
            messagebox.showerror("Error", "Please select a recipe", parent=win)
            return

        recipe_id = recipe_map[recipe_name]

        conn2 = sqlite3.connect("bakery.db")
        cur2 = conn2.cursor()
        cur2.execute("""
            SELECT 
                ri.ingredient_id,
                ri.quantity,      -- required per recipe
                i.quantity,       -- available in inventory
                i.name,
                i.unit,
                i.cost_per_unit
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,))
        rows = cur2.fetchall()

        used_ingredients = []

        # --- CHECK STOCK ---
        for ing_id, req_qty, avail_qty, name, unit, cost_per_unit in rows:
            req_qty = safe_float(req_qty)
            avail_qty = safe_float(avail_qty)

            if avail_qty < req_qty:
                conn2.close()
                messagebox.showerror(
                    "Low Stock",
                    f"Not enough {name}\n\n"
                    f"Available: {avail_qty} {unit}\n"
                    f"Required: {req_qty} {unit}",
                    parent=win
                )
                return

            used_ingredients.append((name, req_qty, unit, cost_per_unit))

        # --- DEDUCT INVENTORY ---
        for ing_id, req_qty, avail_qty, name, unit, cost_per_unit in rows:
            req_qty = safe_float(req_qty)
            avail_qty = safe_float(avail_qty)
            new_qty = avail_qty - req_qty
            if new_qty < 0:
                new_qty = 0
            cur2.execute(
                "UPDATE ingredients SET quantity = ? WHERE id = ?",
                (new_qty, ing_id)
            )

        conn2.commit()
        conn2.close()

        # --- RECEIPT WITH COST ---
        file_path, receipt_text = generate_receipt(recipe_name, used_ingredients)
        show_receipt_preview(win, receipt_text, file_path)

        win.lift()
        win.focus_force()

    tk.Button(
        win,
        text="Make Cake",
        font=("Arial", 12, "bold"),
        width=22,
        command=make_cake
    ).pack(pady=25)
