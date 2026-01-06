import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from utils import center_window


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
            quantity INTEGER,
            customer_name TEXT,
            total REAL,
            receipt_text TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def open_reports():
    ensure_receipts_table()

    win = tk.Toplevel()
    win.title("Owner Reports (Internal Only)")
    center_window(win, 900, 550)
    win.lift()
    win.focus_force()

    tk.Label(
        win,
        text="Owner Reports (Not for Customers)",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    # ===== FILTER SECTION =====
    filter_frame = tk.Frame(win)
    filter_frame.pack(pady=5)

    tk.Label(filter_frame, text="Report Range:", font=("Arial", 11)).grid(row=0, column=0, padx=5)

    range_combo = ttk.Combobox(filter_frame, state="readonly", width=20)
    range_combo["values"] = ("Today", "All Time")
    range_combo.current(0)
    range_combo.grid(row=0, column=1, padx=5)

    tk.Button(
        filter_frame,
        text="Generate Report",
        command=lambda: load_report(),
        width=16
    ).grid(row=0, column=2, padx=5)

    # ===== TABLE =====
    table_frame = tk.Frame(win)
    table_frame.pack(fill="both", expand=True, padx=10, pady=5)

    scroll_y = tk.Scrollbar(table_frame)
    scroll_y.pack(side="right", fill="y")

    scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
    scroll_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(
        table_frame,
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set,
        selectmode="browse"
    )
    tree.pack(fill="both", expand=True)
    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)

    tree["columns"] = ("Recipe", "Qty Sold", "Total Sales", "Est. Cost", "Est. Profit")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("Recipe", anchor=tk.W, width=260)
    tree.column("Qty Sold", anchor=tk.CENTER, width=80)
    tree.column("Total Sales", anchor=tk.CENTER, width=100)
    tree.column("Est. Cost", anchor=tk.CENTER, width=100)
    tree.column("Est. Profit", anchor=tk.CENTER, width=100)

    tree.heading("#0", text="")
    tree.heading("Recipe", text="Recipe")
    tree.heading("Qty Sold", text="Qty Sold")
    tree.heading("Total Sales", text="Total Sales")
    tree.heading("Est. Cost", text="Estimated Cost")
    tree.heading("Est. Profit", text="Estimated Profit")

    tree.tag_configure("even", background="#f3f3ff")
    tree.tag_configure("odd", background="#ffffff")

    # ===== SUMMARY BAR =====
    summary_frame = tk.Frame(win)
    summary_frame.pack(pady=8)

    total_qty_label = tk.Label(summary_frame, text="Total Qty: 0", font=("Arial", 11))
    total_qty_label.grid(row=0, column=0, padx=10)

    total_sales_label = tk.Label(summary_frame, text="Total Sales: 0.00", font=("Arial", 11))
    total_sales_label.grid(row=0, column=1, padx=10)

    total_profit_label = tk.Label(summary_frame, text="Total Est. Profit: 0.00", font=("Arial", 11))
    total_profit_label.grid(row=0, column=2, padx=10)

    # ===== REPORT LOGIC =====

    def load_report():
        # Clear table
        for row in tree.get_children():
            tree.delete(row)

        selected_range = range_combo.get()
        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()

        # Filter receipts based on range
        if selected_range == "Today":
            cur.execute("""
                SELECT recipe_name, SUM(quantity) as total_qty, SUM(total) as total_sales
                FROM receipts
                WHERE date(created_at) = date('now','localtime')
                GROUP BY recipe_name
                ORDER BY recipe_name
            """)
        else:  # All Time
            cur.execute("""
                SELECT recipe_name, SUM(quantity) as total_qty, SUM(total) as total_sales
                FROM receipts
                GROUP BY recipe_name
                ORDER BY recipe_name
            """)

        rows = cur.fetchall()

        # For each recipe, estimate cost using current ingredients + cost_per_unit
        grand_total_qty = 0
        grand_total_sales = 0.0
        grand_total_profit = 0.0

        for i, (recipe_name, total_qty, total_sales) in enumerate(rows):
            # Get recipe id
            cur.execute("SELECT id FROM recipes WHERE name = ?", (recipe_name,))
            rec_row = cur.fetchone()
            if not rec_row:
                est_cost_total = 0.0
            else:
                recipe_id = rec_row[0]
                # Sum cost per cake from ingredients
                cur.execute("""
                    SELECT ri.quantity, i.cost_per_unit
                    FROM recipe_ingredients ri
                    JOIN ingredients i ON ri.ingredient_id = i.id
                    WHERE ri.recipe_id = ?
                """, (recipe_id,))
                ing_rows = cur.fetchall()

                cost_per_cake = 0.0
                for req_qty, cpu in ing_rows:
                    cost_per_cake += safe_float(req_qty) * safe_float(cpu)

                est_cost_total = cost_per_cake * safe_float(total_qty)

            est_profit = safe_float(total_sales) - est_cost_total

            tag = "even" if i % 2 == 0 else "odd"
            tree.insert(
                "",
                tk.END,
                values=(
                    recipe_name,
                    int(total_qty),
                    f"{safe_float(total_sales):.2f}",
                    f"{est_cost_total:.2f}",
                    f"{est_profit:.2f}"
                ),
                tags=(tag,)
            )

            grand_total_qty += safe_float(total_qty)
            grand_total_sales += safe_float(total_sales)
            grand_total_profit += est_profit

        conn.close()

        # Update summary labels
        total_qty_label.config(text=f"Total Qty: {int(grand_total_qty)}")
        total_sales_label.config(text=f"Total Sales: {grand_total_sales:.2f}")
        total_profit_label.config(text=f"Total Est. Profit: {grand_total_profit:.2f}")

        win.lift()
        win.focus_force()

    # Load initial (Today) report
    load_report()

    # Close button
    tk.Button(
        win,
        text="Close",
        width=12,
        command=win.destroy
    ).pack(pady=5)
