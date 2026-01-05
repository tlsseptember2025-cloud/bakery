import tkinter as tk
import sqlite3
from tkinter import messagebox
from datetime import datetime
import os
from utils import center_window

def open_make_cake():
    win = tk.Toplevel()
    win.title("Make Cake")
    center_window(win, 400, 250)
    #win.geometry("400x350")

    tk.Label(win, text="Make Cake 🍰", font=("Arial", 14)).pack(pady=10)

    # --- Connect to DB and get recipes ---
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM recipes")
    recipes = cur.fetchall()
    conn.close()

    if not recipes:
        tk.Label(win, text="No recipes found. Please add recipes first.").pack()
        return

    # --- Tkinter dropdown variable ---
    selected_recipe = tk.StringVar()
    selected_recipe.set(recipes[0][1])  # default value

    # --- Dropdown menu ---
    options = [r[1] for r in recipes]
    tk.Label(win, text="Select Cake:").pack()
    tk.OptionMenu(win, selected_recipe, *options).pack(pady=5)

    # --- Make Cake function ---
    def make_cake():
        recipe_name = selected_recipe.get()
        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()

        # Get recipe ID
        cur.execute("SELECT id FROM recipes WHERE name=?", (recipe_name,))
        recipe_id = cur.fetchone()[0]

        # Get ingredients for recipe (including unit)
        cur.execute("""
        SELECT i.id, i.name, i.quantity, i.alert_level, ri.amount_used, i.unit
        FROM ingredients i
        JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        WHERE ri.recipe_id=?
        """, (recipe_id,))
        items = cur.fetchall()

        # --- Check for insufficient stock ---
        for item in items:
            ingredient_name = item[1]
            available_qty = item[2]
            required_qty = item[4]
            if available_qty < required_qty:
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Not enough {ingredient_name}! Available: {available_qty} {item[5]}, Needed: {required_qty} {item[5]}"
                )
                conn.close()
                return  # Stop making cake

        # --- Deduct stock & prepare receipt ---
        receipt_lines = []
        receipt_lines.append("🍰 Bakery Receipt 🍰")
        receipt_lines.append(f"Cake: {recipe_name}")
        receipt_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        receipt_lines.append("\nIngredients Used:")

        for item in items:
            ingredient_id = item[0]
            ingredient_name = item[1]
            available_qty = item[2]
            alert_level = item[3]
            used_qty = item[4]
            unit = item[5]

            new_qty = available_qty - used_qty
            cur.execute("UPDATE ingredients SET quantity=? WHERE id=?", (new_qty, ingredient_id))

            receipt_lines.append(f"- {ingredient_name}: {used_qty} {unit}")

            # Low stock alert
            if new_qty <= alert_level:
                messagebox.showwarning(
                    "Low Stock Alert",
                    f"{ingredient_name} is running low! Remaining: {new_qty} {unit}"
                )

        conn.commit()
        conn.close()

        # --- Save receipt in receipts/ folder ---
        receipts_folder = "receipts"
        if not os.path.exists(receipts_folder):
            os.makedirs(receipts_folder)

        receipt_filename = os.path.join(
            receipts_folder,
            f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        with open(receipt_filename, "w") as f:
            for line in receipt_lines:
                f.write(line + "\n")

        messagebox.showinfo(
            "Success",
            f"Cake made successfully!\nReceipt saved as:\n{receipt_filename}"
        )

    tk.Button(win, text="Make Cake", command=make_cake, width=25).pack(pady=20)