import tkinter as tk
from PIL import Image, ImageTk

from utils import center_window
from inventory import open_inventory
from recipes import open_recipes
from make_cake import open_make_cake
from receipts_history import open_receipts_history
from reports import open_reports

# --------- HELPER TO LOAD & RESIZE IMAGES ---------

def load_image(path, size):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def main():
    root = tk.Tk()
    root.title("Bakery Shop")

    # Splash-style window size
    center_window(root, 600, 850)
    root.config(bg="#f2ebe3")  # light bakery background

    # ---------- LOAD IMAGES ----------
    # Make sure these images exist in your project folder
    # You can use .png or .png
    logo_img = load_image("images/logo.png", (180, 180))          # app logo in the middle top
    inventory_img = load_image("images/inventory.png", (128, 128))
    recipes_img = load_image("images/recipes.png", (128, 128))
    orders_img = load_image("images/orders.png", (128, 128))
    receipts_img = load_image("images/receipts.png", (128, 128))
    reports_img = load_image("images/reports.png", (128, 128))

    # Keep references so images don’t disappear
    root.image_refs = [logo_img, inventory_img, recipes_img, orders_img, receipts_img, reports_img]

    # ---------- TOP SPLASH HEADER ----------
    header_frame = tk.Frame(root, bg="#f2ebe3")
    header_frame.pack(pady=20)

    # Logo
    logo_label = tk.Label(header_frame, image=logo_img, bg="#f2ebe3")
    logo_label.pack()

    # App title
    title_label = tk.Label(
        header_frame,
        text="Bakery Management System",
        font=("Arial", 24, "bold"),
        bg="#f2ebe3",
        fg="#5a3b24"  # chocolate color
    )
    title_label.pack(pady=10)

    # Subtitle
    subtitle_label = tk.Label(
        header_frame,
        text="Dashboard",
        font=("Arial", 14),
        bg="#f2ebe3",
        fg="#7b5b3b"
    )
    subtitle_label.pack()

    # ---------- MAIN DASHBOARD (2 x 2 GRID) ----------
    dashboard_frame = tk.Frame(root, bg="#f2ebe3")
    dashboard_frame.pack(expand=True, pady=30)

    # INVENTORY (Top-Left)
    inv_frame = tk.Frame(dashboard_frame, bg="#f2ebe3")
    inv_frame.grid(row=0, column=0, padx=60, pady=40)

    tk.Button(
        inv_frame,
        image=inventory_img,
        command=open_inventory,
        bd=0,
        highlightthickness=0,
        activebackground="#f2ebe3",
        bg="#f2ebe3"
    ).pack()
    tk.Label(
        inv_frame,
        text="Inventory",
        font=("Arial", 12, "bold"),
        bg="#f2ebe3",
        fg="#3b2a1a"
    ).pack(pady=6)

    # RECIPES (Top-Right)
    rec_frame = tk.Frame(dashboard_frame, bg="#f2ebe3")
    rec_frame.grid(row=0, column=1, padx=60, pady=40)

    tk.Button(
        rec_frame,
        image=recipes_img,
        command=open_recipes,
        bd=0,
        highlightthickness=0,
        activebackground="#f2ebe3",
        bg="#f2ebe3"
    ).pack()
    tk.Label(
        rec_frame,
        text="Recipes",
        font=("Arial", 12, "bold"),
        bg="#f2ebe3",
        fg="#3b2a1a"
    ).pack(pady=6)



    # MAKE CAKE (Bottom-Left)
    ord_frame = tk.Frame(dashboard_frame, bg="#f2ebe3")
    ord_frame.grid(row=0, column=2, padx=60, pady=40)

    tk.Button(
        ord_frame,
        image=orders_img,
        command=open_make_cake,
        bd=0,
        highlightthickness=0,
        activebackground="#f2ebe3",
        bg="#f2ebe3"
    ).pack()
    tk.Label(
        ord_frame,
        text="Make Cake",
        font=("Arial", 12, "bold"),
        bg="#f2ebe3",
        fg="#3b2a1a"
    ).pack(pady=6)

    # RECEIPTS HISTORY (Bottom-Right)
    recp_frame = tk.Frame(dashboard_frame, bg="#f2ebe3")
    recp_frame.grid(row=1, column=0, padx=60, pady=40)

    tk.Button(
        recp_frame,
        image=receipts_img,
        command=open_receipts_history,
        bd=0,
        highlightthickness=0,
        activebackground="#f2ebe3",
        bg="#f2ebe3"
    ).pack()
    tk.Label(
        recp_frame,
        text="Receipts History",
        font=("Arial", 12, "bold"),
        bg="#f2ebe3",
        fg="#3b2a1a"
    ).pack(pady=6)

    # Reports (Top-Left)
    inv_frame = tk.Frame(dashboard_frame, bg="#f2ebe3")
    inv_frame.grid(row=1, column=1, padx=60, pady=40)

    tk.Button(
        inv_frame,
        image=inventory_img,
        command=open_inventory,
        bd=0,
        highlightthickness=0,
        activebackground="#f2ebe3",
        bg="#f2ebe3"
    ).pack()
    tk.Label(
        inv_frame,
        text="Inventory",
        font=("Arial", 12, "bold"),
        bg="#f2ebe3",
        fg="#3b2a1a"
    ).pack(pady=6)

    # ---------- FOOTER ----------
    footer = tk.Label(
        root,
        text="© 2026 My Bakery | Splash Dashboard",
        font=("Arial", 9),
        bg="#f2ebe3",
        fg="#8c6b4a"
    )
    footer.pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()

