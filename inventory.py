import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from utils import center_window


# ---------- DB HELPER: ensure cost_per_unit column exists ----------

def ensure_cost_column():
    conn = sqlite3.connect("bakery.db")
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(ingredients)")
    cols = [row[1].lower() for row in cur.fetchall()]
    if "cost_per_unit" not in cols:
        cur.execute("ALTER TABLE ingredients ADD COLUMN cost_per_unit REAL DEFAULT 0")
        conn.commit()
    conn.close()


# ============== MAIN INVENTORY WINDOW ==============

def open_inventory():
    ensure_cost_column()  # make sure DB has cost_per_unit

    win = tk.Toplevel()
    win.title("Inventory")
    center_window(win, 900, 550)

    win.lift()
    win.focus_force()

    tk.Label(win, text="Current Inventory", font=("Arial", 16, "bold")).pack(pady=10)

    # ----- TABLE FRAME -----
    table_frame = tk.Frame(win)
    table_frame.pack(fill="both", expand=True, padx=10)

    tree_scroll = tk.Scrollbar(table_frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(table_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
    tree.pack(fill="both", expand=True)
    tree_scroll.config(command=tree.yview)

    tree["columns"] = ("Name", "Quantity", "Unit", "Alert Level", "Cost/Unit")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("Name", anchor=tk.W, width=220)
    tree.column("Quantity", anchor=tk.CENTER, width=90)
    tree.column("Unit", anchor=tk.CENTER, width=70)
    tree.column("Alert Level", anchor=tk.CENTER, width=90)
    tree.column("Cost/Unit", anchor=tk.CENTER, width=100)

    tree.heading("#0", text="")
    tree.heading("Name", text="Ingredient")
    tree.heading("Quantity", text="Quantity")
    tree.heading("Unit", text="Unit")
    tree.heading("Alert Level", text="Alert Level")
    tree.heading("Cost/Unit", text="Cost / Unit")

    tree.tag_configure("low_stock", background="mistyrose")

    # ----- LOAD INVENTORY -----

    def load_inventory():
        for row in tree.get_children():
            tree.delete(row)

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT name, quantity, unit, alert_level, cost_per_unit "
            "FROM ingredients ORDER BY name ASC"
        )
        rows = cur.fetchall()
        conn.close()

        for name, qty, unit, alert, cost_per_unit in rows:
            display_cost = f"{cost_per_unit:.2f}" if isinstance(cost_per_unit, (int, float)) else cost_per_unit
            row_id = tree.insert("", tk.END, values=(name, qty, unit, alert, display_cost))
            try:
                if float(qty) <= float(alert):
                    tree.item(row_id, tags=("low_stock",))
            except Exception:
                pass  # ignore bad data

    load_inventory()

    # ========== ADD NEW INGREDIENT SECTION ==========

    tk.Label(win, text="Add New Ingredient", font=("Arial", 14, "bold")).pack(pady=10)
    form_frame = tk.Frame(win)
    form_frame.pack(pady=5)

    tk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=3, pady=2)
    tk.Label(form_frame, text="Quantity:").grid(row=1, column=0, sticky="e", padx=3, pady=2)
    tk.Label(form_frame, text="Unit:").grid(row=2, column=0, sticky="e", padx=3, pady=2)
    tk.Label(form_frame, text="Alert Level:").grid(row=3, column=0, sticky="e", padx=3, pady=2)
    tk.Label(form_frame, text="Cost per Unit:").grid(row=4, column=0, sticky="e", padx=3, pady=2)

    name_entry = tk.Entry(form_frame, width=22)
    qty_entry = tk.Entry(form_frame, width=22)
    unit_entry = tk.Entry(form_frame, width=22)
    alert_entry = tk.Entry(form_frame, width=22)
    cost_entry = tk.Entry(form_frame, width=22)

    name_entry.grid(row=0, column=1, padx=3, pady=2)
    qty_entry.grid(row=1, column=1, padx=3, pady=2)
    unit_entry.grid(row=2, column=1, padx=3, pady=2)
    alert_entry.grid(row=3, column=1, padx=3, pady=2)
    cost_entry.grid(row=4, column=1, padx=3, pady=2)

    def add_ingredient():
        try:
            name = name_entry.get().strip()
            qty = float(qty_entry.get())
            unit = unit_entry.get().strip()
            alert = float(alert_entry.get())
            cost_per_unit = float(cost_entry.get()) if cost_entry.get().strip() != "" else 0.0

            if not name or not unit:
                messagebox.showerror("Error", "Please enter name and unit.", parent=win)
                win.lift(); win.focus_force()
                return

            conn = sqlite3.connect("bakery.db")
            cur = conn.cursor()

            # check duplicate (case-insensitive)
            cur.execute("SELECT id FROM ingredients WHERE LOWER(name)=?", (name.lower(),))
            if cur.fetchone():
                messagebox.showwarning("Duplicate", f"'{name}' already exists in inventory.", parent=win)
                conn.close()
                win.lift(); win.focus_force()
                return

            cur.execute(
                "INSERT INTO ingredients (name, quantity, unit, alert_level, cost_per_unit) "
                "VALUES (?, ?, ?, ?, ?)",
                (name, qty, unit, alert, cost_per_unit)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"{name} added to inventory.", parent=win)
            load_inventory()

            # clear fields
            name_entry.delete(0, tk.END)
            qty_entry.delete(0, tk.END)
            unit_entry.delete(0, tk.END)
            alert_entry.delete(0, tk.END)
            cost_entry.delete(0, tk.END)

            win.lift(); win.focus_force()

        except ValueError:
            messagebox.showerror("Error", "Quantity, alert level and cost must be numbers.", parent=win)
            win.lift(); win.focus_force()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add ingredient:\n{e}", parent=win)
            win.lift(); win.focus_force()

    tk.Button(
        win,
        text="Add Ingredient",
        command=add_ingredient,
        width=25
    ).pack(pady=5)

    # ========== RESTOCK FROM MAIN INVENTORY ==========

    def restock_item():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an ingredient to restock.", parent=win)
            win.lift(); win.focus_force()
            return

        item = tree.item(selected)
        name = item["values"][0]

        restock_win = tk.Toplevel(win)
        restock_win.title(f"Restock {name}")
        center_window(restock_win, 300, 150)
        restock_win.transient(win)
        restock_win.grab_set()
        restock_win.lift()
        restock_win.focus_force()

        tk.Label(restock_win, text=f"Add quantity for {name}:").pack(pady=10)
        qty_entry_local = tk.Entry(restock_win)
        qty_entry_local.pack(pady=5)

        def confirm_restock():
            try:
                add_qty = float(qty_entry_local.get())
                if add_qty <= 0:
                    messagebox.showerror("Error", "Please enter a positive number.", parent=restock_win)
                    restock_win.lift(); restock_win.focus_force()
                    return

                conn_local = sqlite3.connect("bakery.db")
                cur_local = conn_local.cursor()
                cur_local.execute(
                    "UPDATE ingredients SET quantity = quantity + ? WHERE name=?",
                    (add_qty, name)
                )
                conn_local.commit()
                conn_local.close()

                messagebox.showinfo("Success", f"Added {add_qty} to {name}.", parent=restock_win)
                restock_win.destroy()
                load_inventory()
                win.lift(); win.focus_force()

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.", parent=restock_win)
                restock_win.lift(); restock_win.focus_force()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restock:\n{e}", parent=restock_win)
                restock_win.lift(); restock_win.focus_force()

        tk.Button(restock_win, text="Add Quantity", command=confirm_restock).pack(pady=10)

    # ========== LOW STOCK WINDOW (PHASE 1 FEATURE, STILL WORKS) ==========

    def open_low_stock():
        low_win = tk.Toplevel(win)
        low_win.title("Low Stock Items")
        center_window(low_win, 650, 400)
        low_win.transient(win)
        low_win.grab_set()
        low_win.lift()
        low_win.focus_force()

        tk.Label(low_win, text="Low Stock Ingredients", font=("Arial", 14, "bold")).pack(pady=10)

        table_frame_ls = tk.Frame(low_win)
        table_frame_ls.pack(fill="both", expand=True, padx=10)

        scroll_ls = tk.Scrollbar(table_frame_ls)
        scroll_ls.pack(side="right", fill="y")

        tree_ls = ttk.Treeview(table_frame_ls, yscrollcommand=scroll_ls.set, selectmode="browse")
        tree_ls.pack(fill="both", expand=True)
        scroll_ls.config(command=tree_ls.yview)

        tree_ls["columns"] = ("Name", "Quantity", "Unit", "Alert Level", "Cost/Unit")
        tree_ls.column("#0", width=0, stretch=tk.NO)
        tree_ls.column("Name", anchor=tk.W, width=220)
        tree_ls.column("Quantity", anchor=tk.CENTER, width=90)
        tree_ls.column("Unit", anchor=tk.CENTER, width=70)
        tree_ls.column("Alert Level", anchor=tk.CENTER, width=90)
        tree_ls.column("Cost/Unit", anchor=tk.CENTER, width=100)

        tree_ls.heading("#0", text="")
        tree_ls.heading("Name", text="Ingredient")
        tree_ls.heading("Quantity", text="Quantity")
        tree_ls.heading("Unit", text="Unit")
        tree_ls.heading("Alert Level", text="Alert Level")
        tree_ls.heading("Cost/Unit", text="Cost / Unit")

        tree_ls.tag_configure("low_stock", background="mistyrose")

        def load_low_items():
            for row in tree_ls.get_children():
                tree_ls.delete(row)

            conn2 = sqlite3.connect("bakery.db")
            cur2 = conn2.cursor()
            cur2.execute(
                "SELECT name, quantity, unit, alert_level, cost_per_unit "
                "FROM ingredients "
                "WHERE quantity <= alert_level "
                "ORDER BY name ASC"
            )
            rows2 = cur2.fetchall()
            conn2.close()

            for name, qty, unit, alert, cost_per_unit in rows2:
                display_cost = f"{cost_per_unit:.2f}" if isinstance(cost_per_unit, (int, float)) else cost_per_unit
                tree_ls.insert("", tk.END, values=(name, qty, unit, alert, display_cost), tags=("low_stock",))

        load_low_items()

        def restock_from_low():
            selected = tree_ls.selection()
            if not selected:
                messagebox.showwarning("Select Item", "Please select an ingredient to restock.", parent=low_win)
                low_win.lift(); low_win.focus_force()
                return

            item = tree_ls.item(selected)
            name = item["values"][0]

            restock_win = tk.Toplevel(low_win)
            restock_win.title(f"Restock {name}")
            center_window(restock_win, 300, 150)
            restock_win.transient(low_win)
            restock_win.grab_set()
            restock_win.lift()
            restock_win.focus_force()

            tk.Label(restock_win, text=f"Add quantity for {name}:").pack(pady=10)
            qty_entry_local = tk.Entry(restock_win)
            qty_entry_local.pack(pady=5)

            def confirm_restock_ls():
                try:
                    add_qty = float(qty_entry_local.get())
                    if add_qty <= 0:
                        messagebox.showerror("Error", "Please enter a positive number.", parent=restock_win)
                        restock_win.lift(); restock_win.focus_force()
                        return

                    conn3 = sqlite3.connect("bakery.db")
                    cur3 = conn3.cursor()
                    cur3.execute(
                        "UPDATE ingredients SET quantity = quantity + ? WHERE name=?",
                        (add_qty, name)
                    )
                    conn3.commit()
                    conn3.close()

                    messagebox.showinfo("Success", f"Added {add_qty} to {name}.", parent=restock_win)
                    restock_win.destroy()
                    load_low_items()
                    load_inventory()
                    low_win.lift(); low_win.focus_force()

                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number.", parent=restock_win)
                    restock_win.lift(); restock_win.focus_force()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to restock:\n{e}", parent=restock_win)
                    restock_win.lift(); restock_win.focus_force()

            tk.Button(restock_win, text="Add Quantity", command=confirm_restock_ls).pack(pady=10)

        btn_frame_ls = tk.Frame(low_win, bg=low_win["bg"])
        btn_frame_ls.pack(pady=10)

        tk.Button(btn_frame_ls, text="Restock Selected", width=18, command=restock_from_low).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame_ls, text="Close", width=10, command=low_win.destroy).grid(row=0, column=1, padx=5)

    # ========== BUTTONS UNDER MAIN INVENTORY ==========

    btn_frame_main = tk.Frame(win)
    btn_frame_main.pack(pady=10)

    tk.Button(
        btn_frame_main,
        text="Restock Selected Item",
        width=20,
        command=restock_item
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        btn_frame_main,
        text="Low Stock Items",
        width=20,
        command=open_low_stock
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        btn_frame_main,
        text="Close Inventory",
        width=18,
        command=win.destroy
    ).grid(row=0, column=2, padx=5)




