import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from paths import get_db_path
from utils import center_window


def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0


def ensure_receipts_table():
    conn = sqlite3.connect(get_db_path())
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

    # We'll store current range string to reuse in details
    current_range = {"value": "Today"}

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
        current_range["value"] = selected_range  # remember it
        conn = sqlite3.connect(get_db_path())
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

        grand_total_qty = 0
        grand_total_sales = 0.0
        grand_total_profit = 0.0

        for i, (recipe_name, total_qty, total_sales) in enumerate(rows):
            # Get recipe id (for cost calculation)
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

    # ===== DRILL-DOWN: DETAILS WINDOW =====

    def show_recipe_details(recipe_name):
        """Open a window listing all receipts for this recipe in current range."""
        selected_range = current_range["value"]

        detail = tk.Toplevel(win)
        detail.title(f"Details – {recipe_name}")
        center_window(detail, 800, 450)

        detail.transient(win)
        detail.grab_set()
        detail.lift()
        detail.focus_force()

        tk.Label(
            detail,
            text=f"Receipts for: {recipe_name} ({selected_range})",
            font=("Arial", 14, "bold")
        ).pack(pady=8)

        frame = tk.Frame(detail)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        sy = tk.Scrollbar(frame)
        sy.pack(side="right", fill="y")

        sx = tk.Scrollbar(frame, orient="horizontal")
        sx.pack(side="bottom", fill="x")

        tree_det = ttk.Treeview(
            frame,
            yscrollcommand=sy.set,
            xscrollcommand=sx.set,
            selectmode="browse"
        )
        tree_det.pack(fill="both", expand=True)
        sy.config(command=tree_det.yview)
        sx.config(command=tree_det.xview)

        tree_det["columns"] = ("ID", "Date", "Customer", "Qty", "Total")
        tree_det.column("#0", width=0, stretch=tk.NO)
        tree_det.column("ID", anchor=tk.CENTER, width=60)
        tree_det.column("Date", anchor=tk.CENTER, width=170)
        tree_det.column("Customer", anchor=tk.W, width=220)
        tree_det.column("Qty", anchor=tk.CENTER, width=60)
        tree_det.column("Total", anchor=tk.CENTER, width=90)

        tree_det.heading("#0", text="")
        tree_det.heading("ID", text="ID")
        tree_det.heading("Date", text="Date")
        tree_det.heading("Customer", text="Customer")
        tree_det.heading("Qty", text="Qty")
        tree_det.heading("Total", text="Total")

        tree_det.tag_configure("even", background="#f0fff0")
        tree_det.tag_configure("odd", background="#ffffff")

        # Load receipts for this recipe & range
        conn = sqlite3.connect(get_db_path())
        cur = conn.cursor()

        if selected_range == "Today":
            cur.execute("""
                SELECT id, customer_name, quantity, total, created_at
                FROM receipts
                WHERE recipe_name = ?
                  AND date(created_at) = date('now','localtime')
                ORDER BY datetime(created_at) DESC
            """, (recipe_name,))
        else:  # All Time
            cur.execute("""
                SELECT id, customer_name, quantity, total, created_at
                FROM receipts
                WHERE recipe_name = ?
                ORDER BY datetime(created_at) DESC
            """, (recipe_name,))

        rows = cur.fetchall()
        conn.close()

        for i, (rid, cust, qty, total, created_at) in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            cust_display = cust if cust else "N/A"
            tree_det.insert(
                "",
                tk.END,
                values=(rid, created_at, cust_display, qty, f"{safe_float(total):.2f}"),
                tags=(tag,)
            )

        # ---- Preview full receipt on double-click ----

        def preview_selected_receipt(event=None):
            sel = tree_det.selection()
            if not sel:
                return
            item = tree_det.item(sel[0])
            rec_id = item["values"][0]

            conn2 = sqlite3.connect(get_db_path())
            cur2 = conn2.cursor()
            cur2.execute(
                "SELECT receipt_text FROM receipts WHERE id = ?",
                (rec_id,)
            )
            row = cur2.fetchone()
            conn2.close()

            if not row:
                messagebox.showerror("Error", "Receipt not found in database.", parent=detail)
                detail.lift(); detail.focus_force()
                return

            receipt_text = row[0]

            # Open preview window
            prev = tk.Toplevel(detail)
            prev.title(f"Receipt #{rec_id}")
            center_window(prev, 600, 550)

            prev.transient(detail)
            prev.grab_set()
            prev.lift()
            prev.focus_force()

            tk.Label(prev, text=f"Receipt #{rec_id}", font=("Arial", 14, "bold")).pack(pady=8)

            txt = tk.Text(prev, font=("Courier New", 11), wrap="word", bg="#f9f9f9")
            txt.pack(fill="both", expand=True, padx=10, pady=10)
            txt.insert("1.0", receipt_text)
            txt.config(state="disabled")

            tk.Button(prev, text="Close", width=12, command=prev.destroy).pack(pady=8)

            prev.wait_window()

        tree_det.bind("<Double-1>", preview_selected_receipt)

        tk.Button(detail, text="Close", width=12, command=detail.destroy).pack(pady=5)

    # ===== DOUBLE-CLICK ON SUMMARY ROW TO OPEN DETAILS =====

    def on_tree_double_click(event):
        sel = tree.selection()
        if not sel:
            return
        item = tree.item(sel[0])
        recipe_name = item["values"][0]
        if not recipe_name:
            return
        show_recipe_details(recipe_name)

    tree.bind("<Double-1>", on_tree_double_click)

    # ===== GENERATE BUTTON CALLBACK =====
    def on_generate_click():
        load_report()

    tk.Button(
        filter_frame,
        text="Generate Report",
        command=on_generate_click,
        width=16
    ).grid(row=0, column=2, padx=5)

    # Load initial report (Today)
    load_report()

    # Close button for main window
    tk.Button(
        win,
        text="Close Reports",
        width=14,
        command=win.destroy
    ).pack(pady=5)
