import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import tempfile
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


def print_receipt_text(receipt_text, parent):
    """
    Print a receipt from its text content.
    On Windows: writes to a temporary .txt file and uses os.startfile(..., 'print').
    On other OS: shows info message.
    """
    if os.name == "nt":
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
                tmp.write(receipt_text)
                tmp_path = tmp.name
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not create temporary file:\n{e}", parent=parent)
            return

        try:
            os.startfile(tmp_path, "print")
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not send receipt to printer:\n{e}", parent=parent)
    else:
        messagebox.showinfo(
            "Print",
            "Automatic printing is only supported on Windows.\n"
            "Please copy the receipt text to a text editor and print from there.",
            parent=parent
        )


def open_receipts_history():
    ensure_receipts_table()

    win = tk.Toplevel()
    win.title("Receipts History")
    center_window(win, 900, 500)
    win.lift()
    win.focus_force()

    tk.Label(win, text="Receipts History", font=("Arial", 16, "bold")).pack(pady=10)

    # ---------- FRAME FOR TABLE ----------
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

    tree["columns"] = ("ID", "Recipe Name", "Qty", "Customer", "Total", "Created At")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("ID", anchor=tk.CENTER, width=60)
    tree.column("Recipe Name", anchor=tk.W, width=220)
    tree.column("Qty", anchor=tk.CENTER, width=60)
    tree.column("Customer", anchor=tk.W, width=180)
    tree.column("Total", anchor=tk.CENTER, width=90)
    tree.column("Created At", anchor=tk.CENTER, width=160)

    tree.heading("#0", text="")
    tree.heading("ID", text="ID")
    tree.heading("Recipe Name", text="Recipe Name")
    tree.heading("Qty", text="Qty")
    tree.heading("Customer", text="Customer")
    tree.heading("Total", text="Total")
    tree.heading("Created At", text="Created At")

    tree.tag_configure('evenrow', background='#f0f0ff')
    tree.tag_configure('oddrow', background='#ffffff')

    # ---------- LOAD RECEIPTS ----------
    def load_receipts():
        for row in tree.get_children():
            tree.delete(row)

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, recipe_name, quantity, customer_name, total, created_at
                FROM receipts
                ORDER BY datetime(created_at) DESC
            """)
            rows = cur.fetchall()
        except sqlite3.OperationalError:
            conn.close()
            messagebox.showerror(
                "Error",
                "The 'receipts' table does not exist.\nMake a cake first or ensure DB setup.",
                parent=win
            )
            return

        conn.close()

        for idx, (rid, recipe_name, qty, customer, total, created_at) in enumerate(rows):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            customer_display = customer if customer else "N/A"
            tree.insert(
                "",
                tk.END,
                values=(rid, recipe_name, qty, customer_display, f"{safe_float(total):.2f}", created_at),
                tags=(tag,)
            )

    load_receipts()

    # ---------- PREVIEW FUNCTION ----------
    def preview_selected_receipt():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a receipt to view.", parent=win)
            win.lift(); win.focus_force()
            return

        item = tree.item(selected[0])
        receipt_id = item['values'][0]

        conn = sqlite3.connect("bakery.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT recipe_name, receipt_text, created_at, quantity, customer_name, total
            FROM receipts
            WHERE id = ?
        """, (receipt_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Error", "Receipt not found in database.", parent=win)
            win.lift(); win.focus_force()
            return

        recipe_name, receipt_text, created_at, qty, customer, total = row

        # ----- PREVIEW WINDOW -----
        preview = tk.Toplevel(win)
        preview.title(f"Receipt #{receipt_id} - {recipe_name}")
        center_window(preview, 600, 700)

        preview.transient(win)
        preview.grab_set()
        preview.lift()
        preview.attributes("-topmost", True)
        preview.after(150, lambda: preview.attributes("-topmost", False))
        preview.focus_force()

        tk.Label(
            preview,
            text=f"Receipt #{receipt_id}",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        top_info = f"Recipe: {recipe_name}    |    Qty: {qty}    |    Total: {safe_float(total):.2f}"
        tk.Label(
            preview,
            text=top_info,
            font=("Arial", 10)
        ).pack(pady=2)

        tk.Label(
            preview,
            text=f"Customer: {customer if customer else 'N/A'}",
            font=("Arial", 10)
        ).pack(pady=2)

        tk.Label(
            preview,
            text=f"Date: {created_at}",
            font=("Arial", 10)
        ).pack(pady=2)

        text_box = tk.Text(
            preview,
            font=("Courier New", 11),
            wrap="word",
            bg="#f9f9f9"
        )
        text_box.pack(fill="both", expand=True, padx=10, pady=10)
        text_box.insert("1.0", receipt_text)
        text_box.config(state="disabled")

        # Buttons: Print + Close
        btn_frame = tk.Frame(preview)
        btn_frame.pack(pady=8)

        tk.Button(
            btn_frame,
            text="Print",
            width=12,
            command=lambda: print_receipt_text(receipt_text, preview)
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame,
            text="Close",
            width=12,
            command=preview.destroy
        ).grid(row=0, column=1, padx=5)

        preview.wait_window()

    # ---------- DOUBLE-CLICK TO PREVIEW ----------
    def on_double_click(event):
        preview_selected_receipt()

    tree.bind("<Double-1>", on_double_click)

    # ---------- BUTTONS ----------
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    tk.Button(
        btn_frame,
        text="View Selected Receipt",
        width=22,
        command=preview_selected_receipt
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        btn_frame,
        text="Refresh List",
        width=15,
        command=load_receipts
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        btn_frame,
        text="Close",
        width=12,
        command=win.destroy
    ).grid(row=0, column=2, padx=5)

