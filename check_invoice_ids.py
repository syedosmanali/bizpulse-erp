import sqlite3

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Check the exact invoice ID for BILL-20260207-001
result = cursor.execute("SELECT id, bill_number FROM bills WHERE bill_number = 'BILL-20260207-001'").fetchone()
print('Found invoice:', result)

# Also check all invoices to see the ID format
result = cursor.execute("SELECT id, bill_number FROM bills ORDER BY created_at DESC LIMIT 3").fetchall()
print('\nRecent invoices with IDs:')
for row in result:
    print(f'  ID: {row[0]}')
    print(f'  Bill: {row[1]}')
    print()

conn.close()