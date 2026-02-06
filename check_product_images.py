import sqlite3

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

cursor.execute("SELECT id, name, image_url FROM products WHERE name LIKE '%Oil%' OR name LIKE '%oil%'")
products = cursor.fetchall()

print("Products with 'Oil' in name:")
for product in products:
    print(f"ID: {product[0]}, Name: {product[1]}, Image URL: {product[2]}")

conn.close()
