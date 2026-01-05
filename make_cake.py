import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime
from utils import center_window


# ---------------- HELPER FUNCTIONS ----------------

def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0


def generate_receipt(recipe_name, ingredients):
    os.makedirs("receipts", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"receipts/{recipe_name}_{timestamp}.txt"

    with open(filename, "w") as file:
        file.write("BAKERY RECEIPT\n")
        file.write("=" * 35 + "\n")
        file.write(f"Recipe: {recipe_name}\n")
        file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        file.write("Ingredients Used:\n")

        for name, qty, unit in ingredients:
            file.write(f"- {name}: {qty} {unit}\n")

        file.write("\nThank you!\n")

    return filename


# ---------------- MAIN WINDOW ----------------

def open_make_cake():
    win = tk.Toplevel()
    win.title("Make Cake")
    center_window(win, 600, 450)
    win.lift()
    win.focus_force()

    tk.Label(win, text="Make Cake", font=("Arial", 16, "bold")).pack(pady=15)

    # ---------- LOAD RECIPES ----------
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

    # ---------- MAKE CAKE ----------
    def make_cake():
        recipe_name = recipe_combo.get()

        if not recipe_name:
            messagebox.showerror("Error", "Please select a recipe", parent=win)
            return

        recipe_id = recipe_map[recipe_name]

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                ri.ingredient_id,
                ri.quantity,
                i.quantity,
                i.name,
                i.unit
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,))

        rows = cur.fetchall()

        used_ingredients = []

        # ---------- CHECK INVENTORY ----------
        for ing_id, req_qty, avail_qty, name, unit in rows:
            req_qty = safe_float(req_qty)
            avail_qty = safe_float(avail_qty)

            if avail_qty < req_qty:
                conn.close()
                messagebox.showerror(
                    "Low Stock",
                    f"Not enough {name}\n\n"
                    f"Available: {avail_qty} {unit}\n"
                    f"Required: {req_qty} {unit}",
                    parent=win
                )
                return

            used_ingredients.append((name, req_qty, unit))

        # ---------- DEDUCT INVENTORY ----------
        for ing_id, req_qty, avail_qty, name, unit in rows:
            req_qty = safe_float(req_qty)
            avail_qty = safe_float(avail_qty)

            new_qty = avail_qty - req_qty
            if new_qty < 0:
                new_qty = 0

            cur.execute(
                "UPDATE ingredients SET quantity = ? WHERE id = ?",
                (new_qty, ing_id)
            )

        conn.commit()
        conn.close()

        # ---------- GENERATE RECEIPT ----------
        receipt_file = generate_receipt(recipe_name, used_ingredients)

        messagebox.showinfo(
            "Success",
            f"{recipe_name} prepared successfully!\n\n"
            f"Receipt saved in:\n{receipt_file}",
            parent=win
        )

        win.lift()
        win.focus_force()

    # ---------- BUTTON ----------
    tk.Button(
        win,
        text="Make Cake",
        font=("Arial", 12, "bold"),
        width=22,
        command=make_cake
    ).pack(pady=25)

