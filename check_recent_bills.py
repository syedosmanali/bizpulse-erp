import sqlite3
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

print("=== RECENT BILLS CHECK ===")

# Check bills from today
today = datetime.now().date()
yesterday = today - timedelta(days=1)

cursor.execute("""
    SELECT 
        id,
        bill_number,
        total_amount,
        payment_status,
        created_at
    FROM bills 
    WHERE DATE(created_at) >= ?
    ORDER BY created_at DESC
""", (str(yesterday),))

recent_bills = cursor.fetchall()
print(f"\nBills from last 24 hours:")
for bill in recent_bills:
    print(f"  {bill[1]}: ₹{bill[2]} - {bill[3]} - {bill[4]}")

# Check if there are any payments
cursor.execute("""
    SELECT 
        p.id,
        p.bill_id,
        p.method,
        p.amount,
        p.processed_at,
        b.bill_number
    FROM payments p
    JOIN bills b ON p.bill_id = b.id
    WHERE DATE(p.processed_at) >= ?
    ORDER BY p.processed_at DESC
""", (str(yesterday),))

recent_payments = cursor.fetchall()
print(f"\nPayments from last 24 hours:")
for payment in recent_payments:
    print(f"  {payment[5]}: {payment[2]} ₹{payment[3]} - {payment[4]}")

conn.close()