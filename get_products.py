import sqlite3

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row

products = conn.execute('SELECT id, name FROM products LIMIT 3').fetchall()
print('Available products:')
for p in products:
    print(f'ID: {p["id"]}, Name: {p["name"]}')

conn.close()