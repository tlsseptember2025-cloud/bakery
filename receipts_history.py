import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from utils import center_window


def open_receipts_history():
    # ---------- MAIN WINDOW ----------
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

    # ---------- STYLE ----------
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview",
        font=("Arial", 11),
        rowheight=26,
        borderwidth=1,
        relief="solid"
    )
    style.configure(
        "Treeview.Heading",
        font=("Arial", 11, "bold"),
        borderwidth=1,
        relief="raised"
    )
    style.map('Treeview', background=[('selected', '#347083')], foreground=[('selected', 'white')])

    # ---------- COLUMNS ----------
    tree["columns"] = ("ID", "Recipe Name", "Created At")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("ID", anchor=tk.CENTER, width=60, stretch=False)
    tree.column("Recipe Name", anchor=tk.W, width=250, stretch=True)
    tree.column("Created At", anchor=tk.CENTER, width=200, stretch=False)

    tree.heading("#0", text="")
    tree.heading("ID", text="ID")
    tree.heading("Recipe Name", text="Recipe Name")
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
                SELECT id, recipe_name, created_at
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

        for idx, r in enumerate(rows):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert("", tk.END, values=r, tags=(tag,))

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
            SELECT recipe_name, receipt_text, created_at
            FROM receipts
            WHERE id = ?
        """, (receipt_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Error", "Receipt not found in database.", parent=win)
            return

        recipe_name, receipt_text, created_at = row

        # ----- PREVIEW WINDOW -----
        preview = tk.Toplevel(win)
        preview.title(f"Receipt #{receipt_id} - {recipe_name}")
        center_window(preview, 550, 550)

        preview.transient(win)
        preview.grab_set()
        preview.lift()
        preview.attributes("-topmost", True)
        preview.after(150, lambda: preview.attributes("-topmost", False))
        preview.focus_force()

        tk.Label(
            preview,
            text=f"Receipt for: {recipe_name}",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

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

        tk.Button(
            preview,
            text="Close",
            width=15,
            command=preview.destroy
        ).pack(pady=8)

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
