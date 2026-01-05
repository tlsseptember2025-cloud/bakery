import sqlite3

conn = sqlite3.connect("bakery.db")
cursor = conn.cursor()

# Ingredients table
cursor.execute("""
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity REAL,
    unit TEXT,
    alert_level REAL
)
""")

# Recipes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

# Recipe ↔ Ingredients
cursor.execute("""
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER,
    ingredient_id INTEGER,
    amount_used REAL
)
""")

conn.commit()
conn.close()

print("Database created successfully")