import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

print("=== ALL BILLS CHECK ===")

# Check all bills
cursor.execute("""
    SELECT 
        id,
        bill_number,
        total_amount,
        payment_status,
        created_at,
        DATE(created_at) as bill_date
    FROM bills 
    ORDER BY created_at DESC
    LIMIT 10
""")

all_bills = cursor.fetchall()
print(f"\nAll bills (last 10):")
for bill in all_bills:
    print(f"  {bill[1]}: ₹{bill[2]} - {bill[3]} - {bill[4]} (Date: {bill[5]})")

# Check what date the system thinks is "today"
print(f"\nSystem today: {datetime.now().date()}")

conn.close()