import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from utils import center_window
from paths import get_db_path


def ensure_recipe_table_columns():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(recipes)")
    cols = [c[1].lower() for c in cur.fetchall()]
    if "selling_price" not in cols:
        cur.execute("ALTER TABLE recipes ADD COLUMN selling_price REAL DEFAULT 0")
    conn.commit()
    conn.close()


def open_recipes():
    ensure_recipe_table_columns()

    # ================= WINDOW =================
    win = tk.Toplevel()
    win.title("Recipes")
    center_window(win, 950, 850)
    win.minsize(900, 700)
    win.resizable(True, True)
    win.configure(bg="#f2ebe3")
    win.lift()
    win.focus_force()

    # ================= TITLE =================
    tk.Label(
        win,
        text="Recipes",
        font=("Arial", 18, "bold"),
        bg="#f2ebe3"
    ).pack(pady=10)

    # ================= TOP: RECIPE LIST =================
    list_frame = tk.Frame(win, bg="#f2ebe3")
    list_frame.pack(fill="x", padx=12)

    recipe_tree = ttk.Treeview(
        list_frame,
        columns=("ID", "Name", "Price"),
        show="headings",
        height=8
    )
    recipe_tree.pack(side="left", fill="both", expand=True)

    list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=recipe_tree.yview)
    list_scroll.pack(side="right", fill="y")
    recipe_tree.configure(yscrollcommand=list_scroll.set)

    recipe_tree.heading("ID", text="ID")
    recipe_tree.heading("Name", text="Recipe Name")
    recipe_tree.heading("Price", text="Selling Price")

    recipe_tree.column("ID", width=60, anchor="center")
    recipe_tree.column("Name", width=450, anchor="w")
    recipe_tree.column("Price", width=120, anchor="center")

    def load_recipes():
        recipe_tree.delete(*recipe_tree.get_children())
        conn = sqlite3.connect(get_db_path())
        cur = conn.cursor()
        cur.execute("SELECT id, name, selling_price FROM recipes ORDER BY id")
        rows = cur.fetchall()
        conn.close()
        for r in rows:
            recipe_tree.insert("", "end", values=r)

    load_recipes()

    # ================= SCROLLABLE LOWER SECTION =================
    container = tk.Frame(win, bg="#f2ebe3")
    container.pack(fill="both", expand=True, padx=12, pady=8)

    canvas = tk.Canvas(container, bg="#f2ebe3", highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable = tk.Frame(canvas, bg="#f2ebe3")

    canvas_window = canvas.create_window(
        (0, 0),
        window=scrollable,
        anchor="nw"
    )

    def resize_scrollable(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", resize_scrollable)

    scrollable.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # ================= ADD RECIPE =================
    tk.Label(
        scrollable,
        text="Add New Recipe",
        font=("Arial", 15, "bold"),
        bg="#f2ebe3"
    ).pack(pady=12)

    form = tk.Frame(scrollable, bg="#f2ebe3")
    form.pack()

    tk.Label(form, text="Recipe Name:", bg="#f2ebe3").grid(row=0, column=0, sticky="e", pady=4)
    tk.Label(form, text="Selling Price:", bg="#f2ebe3").grid(row=1, column=0, sticky="e", pady=4)

    name_entry = tk.Entry(form, width=32)
    price_entry = tk.Entry(form, width=15)

    name_entry.grid(row=0, column=1, padx=6)
    price_entry.grid(row=1, column=1, padx=6)

    # ================= INGREDIENTS =================
    tk.Label(
        scrollable,
        text="Ingredients for this Recipe",
        font=("Arial", 13, "bold"),
        bg="#f2ebe3"
    ).pack(pady=12)

    ing_frame = tk.Frame(scrollable, bg="#f2ebe3")
    ing_frame.pack(fill="both", expand=True)

    ing_tree = ttk.Treeview(
        ing_frame,
        columns=("ID", "Name", "Unit", "Qty"),
        show="headings",
        height=16
    )
    ing_tree.pack(side="left", fill="both", expand=True)

    ing_scroll = ttk.Scrollbar(ing_frame, orient="vertical", command=ing_tree.yview)
    ing_scroll.pack(side="right", fill="y")
    ing_tree.configure(yscrollcommand=ing_scroll.set)

    ing_tree.heading("ID", text="ID")
    ing_tree.heading("Name", text="Ingredient")
    ing_tree.heading("Unit", text="Unit")
    ing_tree.heading("Qty", text="Qty")

    ing_tree.column("ID", width=50, anchor="center")
    ing_tree.column("Name", width=450, anchor="w")
    ing_tree.column("Unit", width=80, anchor="center")
    ing_tree.column("Qty", width=80, anchor="center")

    def load_ingredients():
        ing_tree.delete(*ing_tree.get_children())
        conn = sqlite3.connect(get_db_path())
        cur = conn.cursor()
        cur.execute("SELECT id, name, unit FROM ingredients ORDER BY name")
        rows = cur.fetchall()
        conn.close()
        for r in rows:
            ing_tree.insert("", "end", values=(r[0], r[1], r[2], 0))

    load_ingredients()

    # ================= EDIT QTY =================
    def edit_qty(event):
        item = ing_tree.identify_row(event.y)
        col = ing_tree.identify_column(event.x)
        if col != "#4" or not item:
            return

        x, y, w, h = ing_tree.bbox(item, col)
        entry = tk.Entry(ing_tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus()

        def save(_=None):
            try:
                val = float(entry.get())
            except:
                val = 0
            values = list(ing_tree.item(item, "values"))
            values[3] = val
            ing_tree.item(item, values=values)
            entry.destroy()

        entry.bind("<Return>", save)
        entry.bind("<FocusOut>", save)

    ing_tree.bind("<Double-1>", edit_qty)

    # ================= ADD BUTTON =================
    def add_recipe():
        name = name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Recipe name required.", parent=win)
            return

        try:
            price = float(price_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Invalid price.", parent=win)
            return

        ingredients = []
        for row in ing_tree.get_children():
            iid, _, _, qty = ing_tree.item(row, "values")
            try:
                qty = float(qty)
            except:
                qty = 0
            if qty > 0:
                ingredients.append((iid, qty))

        if not ingredients:
            messagebox.showerror("Error", "Add at least one ingredient.", parent=win)
            return

        conn = sqlite3.connect(get_db_path())
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO recipes (name, selling_price) VALUES (?, ?)",
            (name, price)
        )
        recipe_id = cur.lastrowid

        for iid, qty in ingredients:
            cur.execute(
                "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                (recipe_id, iid, qty)
            )

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Recipe '{name}' added.", parent=win)
        name_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        load_recipes()
        load_ingredients()

    tk.Button(
        scrollable,
        text="Add Recipe",
        font=("Arial", 13, "bold"),
        width=22,
        command=add_recipe
    ).pack(pady=18)


