import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from utils import center_window


def ensure_recipe_price_column():
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(recipes)")
    cols = [c[1].lower() for c in cur.fetchall()]

    if "selling_price" not in cols:
        cur.execute("ALTER TABLE recipes ADD COLUMN selling_price REAL DEFAULT 0")

    conn.commit()
    conn.close()


def open_recipes():
    ensure_recipe_price_column()

    win = tk.Toplevel()
    win.title("Recipes")
    center_window(win, 800, 600)

    win.lift()
    win.focus_force()

    tk.Label(win, text="Add Recipe", font=("Arial", 16, "bold")).pack(pady=10)

    form = tk.Frame(win)
    form.pack(pady=10)

    tk.Label(form, text="Recipe Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    tk.Label(form, text="Selling Price:").grid(row=1, column=0, padx=5, pady=5, sticky="e")

    name_entry = tk.Entry(form, width=30)
    price_entry = tk.Entry(form, width=30)

    name_entry.grid(row=0, column=1, padx=5, pady=5)
    price_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(win, text="Select Ingredients", font=("Arial", 12, "bold")).pack(pady=10)

    table_frame = tk.Frame(win)
    table_frame.pack()

    tree = ttk.Treeview(table_frame, columns=("Name", "Qty", "Unit"), show="headings", height=7)
    tree.pack()

    tree.heading("Name", text="Ingredient")
    tree.heading("Qty", text="Required Qty")
    tree.heading("Unit", text="Unit")

    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name, unit FROM ingredients ORDER BY name ASC")
    ing_list = cur.fetchall()
    conn.close()

    ing_dict = {}
    qty_entries = {}

    for i, (ing_id, name, unit) in enumerate(ing_list):
        ing_dict[name] = (ing_id, unit)
        tree.insert("", "end", values=(name, "", unit))

    def add_recipe():
        name = name_entry.get().strip()
        price = price_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Enter recipe name", parent=win)
            return

        try:
            price = float(price) if price != "" else 0
        except:
            messagebox.showerror("Error", "Price must be a number", parent=win)
            return

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()

        cur.execute("INSERT INTO recipes (name, selling_price) VALUES (?, ?)", (name, price))
        recipe_id = cur.lastrowid

        for child in tree.get_children():
            vals = tree.item(child)["values"]
            ing_name = vals[0]

            amount = tk.simpledialog.askfloat(
                "Ingredient Quantity",
                f"Enter required amount for {Ing_name}",
                parent=win
            )

            if amount:
                ing_id, _ = ing_dict[ing_name]
                cur.execute(
                    "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                    (recipe_id, ing_id, amount)
                )

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Recipe Added!", parent=win)

    tk.Button(win, text="Save Recipe", command=add_recipe, width=20).pack(pady=20)

