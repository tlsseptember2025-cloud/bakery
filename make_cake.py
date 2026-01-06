import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import tempfile
from datetime import datetime
from utils import center_window


# ===================== HELPERS =====================

def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0


def ensure_receipts_table():
    """Make sure receipts table exists with needed columns."""
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
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


def save_receipt_to_db(recipe_name, qty, customer_name, total, receipt_text):
    ensure_receipts_table()
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO receipts (recipe_name, quantity, customer_name, total, receipt_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        recipe_name,
        qty,
        customer_name,
        total,
        receipt_text,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def ensure_cost_column():
    """Ensure ingredients has cost_per_unit column (for internal use later if needed)."""
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(ingredients)")
    cols = [r[1].lower() for r in cur.fetchall()]
    if "cost_per_unit" not in cols:
        cur.execute("ALTER TABLE ingredients ADD COLUMN cost_per_unit REAL DEFAULT 0")
        conn.commit()
    conn.close()


def print_receipt_file(file_path, receipt_text, parent):
    """
    Try to send a receipt to the printer.
    On Windows: uses os.startfile(..., 'print').
    If file_path doesn't exist, we create a temporary file from receipt_text.
    On other OS: show info message.
    """
    if os.name == "nt":  # Windows
        path_to_print = file_path

        # If file does not exist, create a temporary one
        if not path_to_print or not os.path.exists(path_to_print):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
                    tmp.write(receipt_text)
                    path_to_print = tmp.name
            except Exception as e:
                messagebox.showerror("Print Error", f"Could not create temporary file:\n{e}", parent=parent)
                return

        try:
            os.startfile(path_to_print, "print")
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not send receipt to printer:\n{e}", parent=parent)
    else:
        messagebox.showinfo(
            "Print",
            "Automatic printing is only supported on Windows.\n"
            "Please open the receipt text file and print it from your text editor.",
            parent=parent
        )


def generate_receipt(recipe_name, qty, customer_name, selling_price, ingredients_used):
    """
    ingredients_used: list of (name, qty_used, unit, cost_per_unit)
    Customer receipt: NO cost, NO profit shown.
    """
    os.makedirs("receipts", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"receipts/{recipe_name}_{timestamp}.txt"

    total_sale = selling_price * qty
    lines = []

    lines.append("BAKERY RECEIPT")
    lines.append("=" * 35)
    lines.append(f"Recipe      : {recipe_name}")
    lines.append(f"Customer    : {customer_name if customer_name else 'N/A'}")
    lines.append(f"Quantity    : {qty}")
    lines.append(f"Price/Cake  : {selling_price:.2f}")
    lines.append(f"Total Sale  : {total_sale:.2f}")
    lines.append("")
    lines.append("Ingredients Used:")

    for name, qty_used, unit, cpu in ingredients_used:
        qty_used = safe_float(qty_used)
        lines.append(f"- {name}: {qty_used} {unit}")

    lines.append("")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("Thank you!")

    receipt_text = "\n".join(lines)

    # Save to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(receipt_text)

    # Save to DB (total sale only, no profit)
    save_receipt_to_db(recipe_name, qty, customer_name, total_sale, receipt_text)

    return file_path, receipt_text


def show_receipt_preview(parent, receipt_text, file_path):
    preview = tk.Toplevel(parent)
    preview.title("Receipt Preview")
    center_window(preview, 550, 650)

    preview.transient(parent)
    preview.grab_set()
    preview.lift()
    preview.attributes("-topmost", True)
    preview.after(150, lambda: preview.attributes("-topmost", False))
    preview.focus_force()

    tk.Label(preview, text="Receipt Preview", font=("Arial", 14, "bold")).pack(pady=10)

    text_box = tk.Text(preview, font=("Courier New", 11), wrap="word", bg="#f9f9f9")
    text_box.pack(fill="both", expand=True, padx=10, pady=10)
    text_box.insert("1.0", receipt_text)
    text_box.config(state="disabled")

    tk.Label(preview, text=f"Saved to: {file_path}", font=("Arial", 9)).pack(pady=5)

    # --- Buttons frame: Print + Close ---
    btn_frame = tk.Frame(preview)
    btn_frame.pack(pady=10)

    tk.Button(
        btn_frame,
        text="Print",
        width=12,
        command=lambda: print_receipt_file(file_path, receipt_text, preview)
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        btn_frame,
        text="Close",
        width=12,
        command=preview.destroy
    ).grid(row=0, column=1, padx=5)

    preview.wait_window()


# ===================== MAIN WINDOW =====================

def open_make_cake():
    ensure_cost_column()
    ensure_receipts_table()

    win = tk.Toplevel()
    win.title("Make Cake")
    center_window(win, 650, 520)
    win.lift()
    win.focus_force()

    tk.Label(win, text="Make Cake", font=("Arial", 16, "bold")).pack(pady=10)

    # --- Recipe selection ---
    tk.Label(win, text="Select Recipe", font=("Arial", 12)).pack()
    recipe_combo = ttk.Combobox(win, width=35, state="readonly")
    recipe_combo.pack(pady=5)

    # --- Quantity ---
    tk.Label(win, text="Quantity (number of cakes)", font=("Arial", 12)).pack()
    qty_entry = tk.Entry(win, width=20)
    qty_entry.pack(pady=5)

    # --- Customer Name ---
    tk.Label(win, text="Customer Name (optional)", font=("Arial", 12)).pack()
    customer_entry = tk.Entry(win, width=35)
    customer_entry.pack(pady=5)

    # Load recipes into combo
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM recipes ORDER BY name ASC")
    recipes = cur.fetchall()
    conn.close()

    recipe_map = {name: rid for rid, name in recipes}
    recipe_combo["values"] = list(recipe_map.keys())

    def make_cake():
        recipe_name = recipe_combo.get().strip()
        qty_text = qty_entry.get().strip()
        customer_name = customer_entry.get().strip()

        if not recipe_name or not qty_text:
            messagebox.showerror("Error", "Please select a recipe and enter quantity.", parent=win)
            win.lift(); win.focus_force()
            return

        try:
            qty = int(qty_text)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive whole number.", parent=win)
            win.lift(); win.focus_force()
            return

        recipe_id = recipe_map[recipe_name]

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()

        # Get selling price
        cur.execute("SELECT selling_price FROM recipes WHERE id = ?", (recipe_id,))
        row = cur.fetchone()
        selling_price = safe_float(row[0]) if row else 0.0

        # Get ingredients needed and inventory + cost
        cur.execute("""
            SELECT 
                ri.ingredient_id,
                ri.quantity,       -- required per 1 cake
                i.quantity,        -- available in stock
                i.name,
                i.unit,
                i.cost_per_unit
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,))
        rows = cur.fetchall()

        if not rows:
            conn.close()
            messagebox.showerror("Error", "This recipe has no ingredients linked.", parent=win)
            win.lift(); win.focus_force()
            return

        # --- Check stock ---
        for ing_id, req_per_cake, avail_qty, name, unit, cpu in rows:
            req_per_cake = safe_float(req_per_cake)
            avail_qty = safe_float(avail_qty)
            total_required = req_per_cake * qty

            if avail_qty < total_required:
                conn.close()
                messagebox.showerror(
                    "Low Stock",
                    f"Not enough {name}\n\n"
                    f"Available: {avail_qty} {unit}\n"
                    f"Required for {qty} cake(s): {total_required} {unit}",
                    parent=win
                )
                win.lift(); win.focus_force()
                return

        # --- Deduct inventory ---
        used_ingredients_for_receipt = []
        for ing_id, req_per_cake, avail_qty, name, unit, cpu in rows:
            req_per_cake = safe_float(req_per_cake)
            avail_qty = safe_float(avail_qty)
            total_required = req_per_cake * qty
            new_qty = avail_qty - total_required
            if new_qty < 0:
                new_qty = 0

            cur.execute(
                "UPDATE ingredients SET quantity = ? WHERE id = ?",
                (new_qty, ing_id)
            )

            used_ingredients_for_receipt.append((name, total_required, unit, cpu))

        conn.commit()
        conn.close()

        # --- Generate and show receipt (with Print button) ---
        file_path, receipt_text = generate_receipt(
            recipe_name,
            qty,
            customer_name,
            selling_price,
            used_ingredients_for_receipt
        )

        show_receipt_preview(win, receipt_text, file_path)

        # Reset quantity & customer
        qty_entry.delete(0, tk.END)
        customer_entry.delete(0, tk.END)
        win.lift()
        win.focus_force()

    tk.Button(
        win,
        text="Make Cake",
        font=("Arial", 12, "bold"),
        width=22,
        command=make_cake
    ).pack(pady=20)

