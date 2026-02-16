import sqlite3

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Get recent bills to see the date format
result = cursor.execute('''
    SELECT bill_number, total_amount, credit_balance, is_credit, created_at 
    FROM bills 
    ORDER BY created_at DESC 
    LIMIT 5
''').fetchall()

print("Recent bills:")
for row in result:
    print(f"  Bill: {row[0]}, Amount: {row[1]}, Credit: {row[2]}, Is_Credit: {row[3]}, Created: {row[4]}")

# Check what date the bill from today actually has
today_bills = cursor.execute('''
    SELECT bill_number, total_amount, credit_balance, is_credit, created_at, DATE(created_at) as date_only
    FROM bills 
    WHERE bill_number = 'BILL-20260210-2cc6399c'
''').fetchall()

print(f"\nSpecific bill check:")
for row in today_bills:
    print(f"  Bill: {row[0]}")
    print(f"  Created: {row[4]}")
    print(f"  Date extracted: {row[5]}")

conn.close()