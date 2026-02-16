import sqlite3

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()
today = '2026-02-10'

# Test the exact query used in dashboard service
result = cursor.execute('''
    SELECT 
        COALESCE(SUM(credit_balance), 0) as receivable
    FROM bills 
    WHERE DATE(created_at) = ? 
    AND is_credit = 1
    AND credit_balance > 0
''', [today]).fetchone()

print(f"Today's receivable sum: {result[0] if result else 'None'}")

# Check individual bills
bills = cursor.execute('''
    SELECT bill_number, total_amount, credit_balance, is_credit, created_at
    FROM bills 
    WHERE DATE(created_at) = ?
''', [today]).fetchall()

print(f"\nAll bills from today ({len(bills)}):")
for bill in bills:
    print(f"  Bill: {bill[0]}, Amount: {bill[1]}, Credit: {bill[2]}, Is_Credit: {bill[3]}")

conn.close()