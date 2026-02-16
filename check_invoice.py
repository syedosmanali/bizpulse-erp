import sqlite3

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Check if the specific invoice exists
result = cursor.execute('SELECT id, bill_number, created_at FROM bills WHERE id = ?', ('574b342a-3c57-4376-8c29-6e52537cc0b3',)).fetchone()
print('Specific invoice check:')
print('Invoice found:', result)

# Get recent invoices
result = cursor.execute('SELECT id, bill_number, created_at FROM bills ORDER BY created_at DESC LIMIT 5').fetchall()
print('\nRecent invoices:')
for row in result:
    print(f'  ID: {row[0][:8]}..., Bill: {row[1]}, Date: {row[2]}')

conn.close()