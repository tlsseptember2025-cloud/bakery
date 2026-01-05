import tkinter as tk
from inventory import open_inventory
from recipes import open_recipes
from make_cake import open_make_cake
from utils import center_window
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Bakery Shop Dashboard")
center_window(root, 800, 600)

# Optional: set background color
root.config(bg="#f5f5f5")

# --- Function to load and resize images ---
def load_image(path, size=(128, 128)):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)  # <-- use LANCZOS instead of ANTIALIAS
    return ImageTk.PhotoImage(img)

# --- Load images ---
inventory_img = load_image("images/inventory.png")
recipes_img = load_image("images/recipes.png")
orders_img = load_image("images/orders.png")

# Keep references to prevent garbage collection
image_refs = [inventory_img, recipes_img, orders_img]

# --- Dashboard Frame ---
dashboard_frame = tk.Frame(root, bg="#f5f5f5")
dashboard_frame.pack(expand=True)

# --- Inventory Button ---
inv_frame = tk.Frame(dashboard_frame, bg="#f5f5f5")
inv_frame.grid(row=0, column=0, padx=40, pady=40)
tk.Button(inv_frame, image=inventory_img, command=open_inventory, bd=0).pack()
tk.Label(inv_frame, text="Inventory", font=("Arial", 12, "bold"), bg="#f5f5f5").pack()

# --- Recipes Button ---
rec_frame = tk.Frame(dashboard_frame, bg="#f5f5f5")
rec_frame.grid(row=0, column=1, padx=40, pady=40)
tk.Button(rec_frame, image=recipes_img, command=open_recipes, bd=1).pack()
tk.Label(rec_frame, text="Recipes", font=("Arial", 12, "bold"), bg="#f5f5f5").pack()

# --- Orders Button ---
ord_frame = tk.Frame(dashboard_frame, bg="#f5f5f5")
ord_frame.grid(row=0, column=2, padx=40, pady=40)
tk.Button(ord_frame, image=orders_img, command=open_make_cake, bd=2).pack()
tk.Label(ord_frame, text="Orders", font=("Arial", 12, "bold"), bg="#f5f5f5").pack()

root.mainloop()
