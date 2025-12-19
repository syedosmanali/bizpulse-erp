import sqlite3

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

print("Fixing negative stock...")

# Check negative stock products
cursor.execute('SELECT id, name, stock FROM products WHERE stock < 0')
negative_products = cursor.fetchall()

if negative_products:
    print("Products with negative stock:")
    for product in negative_products:
        print(f"  - {product[1]}: {product[2]}")
    
    # Fix negative stock - set to 0
    cursor.execute('UPDATE products SET stock = 0 WHERE stock < 0')
    print("\n✅ Fixed all negative stock to 0")
else:
    print("✅ No negative stock found")

# Also fix Rice specifically
cursor.execute('UPDATE products SET stock = 10 WHERE name LIKE "Rice%" AND stock <= 0')
print("✅ Set Rice stock to 10")

conn.commit()
conn.close()

print("✅ Stock fix complete!")