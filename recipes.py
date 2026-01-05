import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from utils import center_window

def open_recipes():
    # --- Recipe Window ---
    win = tk.Toplevel()
    win.title("Recipes")
    center_window(win, 850, 800)
    win.lift()
    win.focus_force()
    win.attributes("-topmost", True)
    win.attributes("-topmost", False)

    tk.Label(win, text="Recipes", font=("Arial", 16, "bold")).pack(pady=10)

    # --- Frame for recipe list ---
    list_frame = tk.Frame(win)
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    list_scroll = tk.Scrollbar(list_frame)
    list_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(list_frame, yscrollcommand=list_scroll.set, selectmode="browse")
    tree.pack(fill="both", expand=True)
    list_scroll.config(command=tree.yview)

    # --- Style the Treeview for professional look ---
    style = ttk.Style()
    style.theme_use("clam")  # cleaner style
    style.configure("Treeview",
                    font=("Arial", 12),
                    rowheight=17,
                    borderwidth=1,
                    relief="solid")
    style.configure("Treeview.Heading",
                    font=("Arial", 12, "bold"),
                    borderwidth=1,
                    relief="raised")
    style.map('Treeview', background=[('selected', '#347083')], foreground=[('selected', 'white')])

    # --- Columns ---
    tree['columns'] = ("ID", "Recipe Name")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("ID", anchor=tk.CENTER, width=50, stretch=False)
    tree.column("Recipe Name", anchor=tk.CENTER, width=400, stretch=True)
    tree.heading("#0", text="")
    tree.heading("ID", text="ID")
    tree.heading("Recipe Name", text="Recipe Name")

    # --- Load recipes with zebra stripes ---
    def load_recipes():
        for row in tree.get_children():
            tree.delete(row)

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM recipes ORDER BY id ASC")
        recipes = cur.fetchall()
        conn.close()

        for idx, r in enumerate(recipes):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert("", tk.END, values=r, tags=(tag,))

    tree.tag_configure('evenrow', background='#f0f0ff')
    tree.tag_configure('oddrow', background='#ffffff')

    load_recipes()

    # --- Add New Recipe Section ---
    tk.Label(win, text="Add New Recipe", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(win, text="Recipe Name:").pack()
    recipe_entry = tk.Entry(win, width=30, font=("Arial", 12))
    recipe_entry.pack(pady=5)

    # --- Ingredients Treeview ---
    tk.Label(win, text="Select Ingredients and Quantity:").pack(pady=10)
    ing_frame = tk.Frame(win)
    ing_frame.pack(fill="both", expand=True, padx=10, pady=5)

    ing_scroll = tk.Scrollbar(ing_frame)
    ing_scroll.pack(side="right", fill="y")

    ing_tree = ttk.Treeview(ing_frame, yscrollcommand=ing_scroll.set, selectmode="browse")
    ing_tree.pack(fill="both", expand=True)
    ing_scroll.config(command=ing_tree.yview)

    ing_tree['columns'] = ("ID", "Name", "Unit", "Qty")
    ing_tree.column("#0", width=0, stretch=tk.NO)
    ing_tree.column("ID", anchor=tk.CENTER, width=50, stretch=False)
    ing_tree.column("Name", anchor=tk.CENTER, width=150, stretch=True)
    ing_tree.column("Unit", anchor=tk.CENTER, width=80, stretch=False)
    ing_tree.column("Qty", anchor=tk.CENTER, width=120, stretch=False)
    ing_tree.heading("#0", text="")
    ing_tree.heading("ID", text="ID")
    ing_tree.heading("Name", text="Ingredient")
    ing_tree.heading("Unit", text="Unit")
    ing_tree.heading("Qty", text="Qty for Recipe")

    # --- Load ingredients with zebra stripes ---
    def load_ingredients():
        for row in ing_tree.get_children():
            ing_tree.delete(row)

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()
        cur.execute("SELECT id, name, unit FROM ingredients ORDER BY id ASC")
        ingredients = cur.fetchall()
        conn.close()

        for idx, ing in enumerate(ingredients):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            ing_tree.insert("", tk.END, values=(ing[0], ing[1], ing[2], 0), tags=(tag,))

    ing_tree.tag_configure('evenrow', background='#f0fff0')
    ing_tree.tag_configure('oddrow', background='#ffffff')

    load_ingredients()

    # --- Double-click to edit Qty ---
    def on_double_click(event):
        item = ing_tree.identify_row(event.y)
        if item:
            col = ing_tree.identify_column(event.x)
            if col == "#4":  # Qty column
                x, y, width, height = ing_tree.bbox(item, col)
                entry = tk.Entry(ing_tree)
                entry.place(x=x, y=y, width=width, height=height)
                entry.focus()

                def save_qty(event):
                    try:
                        value = float(entry.get())
                    except ValueError:
                        value = 0
                    values = list(ing_tree.item(item, 'values'))
                    values[3] = value
                    ing_tree.item(item, values=values)
                    entry.destroy()

                entry.bind("<Return>", save_qty)
                entry.bind("<FocusOut>", save_qty)

    ing_tree.bind("<Double-1>", on_double_click)

    # --- Add Recipe Function ---
    def add_recipe():
        recipe_name = recipe_entry.get().strip()
        if not recipe_name:
            messagebox.showerror("Error", "Enter recipe name", parent=win)
            win.lift(); win.focus_force()
            return

        ingredients_list = []
        for row_id in ing_tree.get_children():
            row = ing_tree.item(row_id)['values']
            ing_id, name, unit, qty = row
            try:
                qty = float(qty)
            except ValueError:
                qty = 0
            if qty > 0:
                ingredients_list.append({'ingredient_id': ing_id, 'quantity': qty, 'unit': unit})

        if not ingredients_list:
            messagebox.showerror("Error", "Enter quantity for at least one ingredient.", parent=win)
            win.lift(); win.focus_force()
            return

        try:
            conn = sqlite3.connect("bakery.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO recipes (name) VALUES (?)", (recipe_name,))
            recipe_id = cur.lastrowid

            for ing in ingredients_list:
                cur.execute(
                    "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit) VALUES (?, ?, ?, ?)",
                    (recipe_id, ing['ingredient_id'], ing['quantity'], ing['unit'])
                )

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Recipe '{recipe_name}' added!", parent=win)
            win.lift(); win.focus_force()
            recipe_entry.delete(0, tk.END)
            load_recipes()

            # Reset ingredient quantities
            for row_id in ing_tree.get_children():
                row = ing_tree.item(row_id, 'values')
                ing_tree.item(row_id, values=(row[0], row[1], row[2], 0))

        except sqlite3.IntegrityError:
            messagebox.showwarning("Duplicate", f"Recipe '{recipe_name}' exists!", parent=win)
            win.lift(); win.focus_force()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add recipe:\n{e}", parent=win)
            win.lift(); win.focus_force()

    tk.Button(win, text="Add Recipe", command=add_recipe, width=25, font=("Arial", 12, "bold")).pack(pady=10)

