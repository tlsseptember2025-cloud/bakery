import tkinter as tk
from inventory import open_inventory
from recipes import open_recipes
from make_cake import open_make_cake
from utils import center_window

app = tk.Tk()
app.title("Bakery Management System")
center_window(app, 400, 250)
#app.geometry("400x400")

tk.Label(
    app,
    text="🍰 Bakery Dashboard",
    font=("Arial", 18, "bold")
).pack(pady=30)

tk.Button(app, text="Inventory", width=25, command=open_inventory).pack(pady=5)
tk.Button(app, text="Recipes", width=25, command=open_recipes).pack(pady=5)
tk.Button(app, text="Make Cake", width=25, command=open_make_cake).pack(pady=5)

app.mainloop()