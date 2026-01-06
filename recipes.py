import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from utils import center_window


def ensure_recipe_table_columns():
    """Make sure recipes table has selling_price column."""
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(recipes)")
    cols = [c[1].lower() for c in cur.fetchall()]

    if "selling_price" not in cols:
        cur.execute("ALTER TABLE recipes ADD COLUMN selling_price REAL DEFAULT 0")

    conn.commit()
    conn.close()


def open_recipes():
    ensure_recipe_table_columns()

    win = tk.Toplevel()
    win.title("Recipes")
    center_window(win, 900, 600)
    win.lift()
    win.focus_force()

    # ---------- TITLE ----------
    tk.Label(win, text="Recipes", font=("Arial", 16, "bold")).pack(pady=10)

    # ---------- RECIPE LIST (TOP TABLE) ----------
    list_frame = tk.Frame(win)
    list_frame.pack(fill="both", expand=False, padx=10, pady=5)

    list_scroll_y = tk.Scrollbar(list_frame)
    list_scroll_y.pack(side="right", fill="y")

    list_scroll_x = tk.Scrollbar(list_frame, orient="horizontal")
    list_scroll_x.pack(side="bottom", fill="x")

    recipe_tree = ttk.Treeview(
        list_frame,
        yscrollcommand=list_scroll_y.set,
        xscrollcommand=list_scroll_x.set,
        selectmode="browse"
    )
    recipe_tree.pack(fill="both", expand=True)

    list_scroll_y.config(command=recipe_tree.yview)
    list_scroll_x.config(command=recipe_tree.xview)

    recipe_tree["columns"] = ("ID", "Name", "Price")
    recipe_tree.column("#0", width=0, stretch=tk.NO)
    recipe_tree.column("ID", anchor=tk.CENTER, width=60)
    recipe_tree.column("Name", anchor=tk.W, width=300)
    recipe_tree.column("Price", anchor=tk.CENTER, width=120)

    recipe_tree.heading("#0", text="")
    recipe_tree.heading("ID", text="ID")
    recipe_tree.heading("Name", text="Recipe Name")
    recipe_tree.heading("Price", text="Selling Price")

    recipe_tree.tag_configure("even", background="#f0f0ff")
    recipe_tree.tag_configure("odd", background="#ffffff")

    def load_recipes():
        for row in recipe_tree.get_children():
            recipe_tree.delete(row)

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()
        cur.execute("SELECT id, name, selling_price FROM recipes ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()

        for i, (rid, name, price) in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            price_display = f"{price:.2f}" if price is not None else "0.00"
            recipe_tree.insert("", tk.END, values=(rid, name, price_display), tags=(tag,))

    load_recipes()

    # ---------- ADD NEW RECIPE SECTION ----------
    tk.Label(win, text="Add New Recipe", font=("Arial", 14, "bold")).pack(pady=8)

    form_frame = tk.Frame(win)
    form_frame.pack(pady=5)

    tk.Label(form_frame, text="Recipe Name:").grid(row=0, column=0, padx=5, pady=3, sticky="e")
    tk.Label(form_frame, text="Selling Price:").grid(row=1, column=0, padx=5, pady=3, sticky="e")

    name_entry = tk.Entry(form_frame, width=30)
    price_entry = tk.Entry(form_frame, width=15)

    name_entry.grid(row=0, column=1, padx=5, pady=3, sticky="w")
    price_entry.grid(row=1, column=1, padx=5, pady=3, sticky="w")

    # ---------- INGREDIENTS TABLE FOR THIS RECIPE ----------
    tk.Label(win, text="Select Ingredients and Quantities for this Recipe", font=("Arial", 12, "bold")).pack(pady=10)

    ing_frame = tk.Frame(win)
    ing_frame.pack(fill="both", expand=True, padx=10, pady=5)

    ing_scroll_y = tk.Scrollbar(ing_frame)
    ing_scroll_y.pack(side="right", fill="y")

    ing_tree = ttk.Treeview(ing_frame, yscrollcommand=ing_scroll_y.set, selectmode="browse")
    ing_tree.pack(fill="both", expand=True)
    ing_scroll_y.config(command=ing_tree.yview)

    ing_tree["columns"] = ("ID", "Name", "Unit", "Qty")
    ing_tree.column("#0", width=0, stretch=tk.NO)
    ing_tree.column("ID", anchor=tk.CENTER, width=50)
    ing_tree.column("Name", anchor=tk.W, width=250)
    ing_tree.column("Unit", anchor=tk.CENTER, width=80)
    ing_tree.column("Qty", anchor=tk.CENTER, width=80)

    ing_tree.heading("#0", text="")
    ing_tree.heading("ID", text="ID")
    ing_tree.heading("Name", text="Ingredient")
    ing_tree.heading("Unit", text="Unit")
    ing_tree.heading("Qty", text="Qty for Recipe")

    ing_tree.tag_configure("even", background="#f0fff0")
    ing_tree.tag_configure("odd", background="#ffffff")

    def load_ingredients():
        for row in ing_tree.get_children():
            ing_tree.delete(row)

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()
        cur.execute("SELECT id, name, unit FROM ingredients ORDER BY name ASC")
        rows = cur.fetchall()
        conn.close()

        for i, (iid, name, unit) in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            # default quantity = 0
            ing_tree.insert("", tk.END, values=(iid, name, unit, 0), tags=(tag,))

    load_ingredients()

    # ---------- EDIT QTY BY DOUBLE-CLICK ----------
    def on_ing_double_click(event):
        item = ing_tree.identify_row(event.y)
        col = ing_tree.identify_column(event.x)

        if not item or col != "#4":  # only allow editing Qty column
            return

        x, y, width, height = ing_tree.bbox(item, col)
        entry = tk.Entry(ing_tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus()

        def save_qty(e=None):
            try:
                val = float(entry.get())
            except:
                val = 0
            vals = list(ing_tree.item(item, "values"))
            vals[3] = val
            ing_tree.item(item, values=vals)
            entry.destroy()

        entry.bind("<Return>", save_qty)
        entry.bind("<FocusOut>", save_qty)

    ing_tree.bind("<Double-1>", on_ing_double_click)

    # ---------- ADD RECIPE BUTTON ----------
    def add_recipe():
        name = name_entry.get().strip()
        price_text = price_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Please enter a recipe name.", parent=win)
            win.lift(); win.focus_force()
            return

        try:
            selling_price = float(price_text) if price_text != "" else 0.0
        except ValueError:
            messagebox.showerror("Error", "Selling price must be a number.", parent=win)
            win.lift(); win.focus_force()
            return

        # Collect ingredients with qty > 0
        ing_for_recipe = []
        for row_id in ing_tree.get_children():
            row_vals = ing_tree.item(row_id, "values")
            ing_id, ing_name, unit, qty = row_vals
            try:
                qty = float(qty)
            except:
                qty = 0
            if qty > 0:
                ing_for_recipe.append((ing_id, qty))

        if not ing_for_recipe:
            messagebox.showerror("Error", "Enter quantity for at least one ingredient.", parent=win)
            win.lift(); win.focus_force()
            return

        try:
            conn = sqlite3.connect("bakery.db")
            cur = conn.cursor()

            # Insert recipe
            cur.execute(
                "INSERT INTO recipes (name, selling_price) VALUES (?, ?)",
                (name, selling_price)
            )
            recipe_id = cur.lastrowid

            # Insert linked ingredients
            for ing_id, qty in ing_for_recipe:
                cur.execute(
                    "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                    (recipe_id, ing_id, qty)
                )

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Recipe '{name}' added.", parent=win)

            # Clear fields
            name_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            load_recipes()
            load_ingredients()  # reset ingredient table back to 0

            win.lift(); win.focus_force()

        except sqlite3.IntegrityError:
            messagebox.showwarning("Duplicate", f"Recipe '{name}' already exists.", parent=win)
            win.lift(); win.focus_force()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add recipe:\n{e}", parent=win)
            win.lift(); win.focus_force()

    tk.Button(
        win,
        text="Add Recipe",
        width=20,
        font=("Arial", 12, "bold"),
        command=add_recipe
    ).pack(pady=10)


