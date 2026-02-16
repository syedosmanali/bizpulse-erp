import sqlite3

# Connect to database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Check recent bills
print("Recent bills:")
cursor.execute("SELECT bill_number, total_amount, created_at FROM bills ORDER BY created_at DESC LIMIT 5")
bills = cursor.fetchall()
for bill in bills:
    print(f"  {bill[0]}: ₹{bill[1]} - {bill[2]}")

# Delete today's bills
print("\nDeleting today's bills...")
cursor.execute("DELETE FROM bills WHERE DATE(created_at) = '2026-02-10'")
deleted = cursor.rowcount
print(f"Deleted {deleted} bills")

conn.commit()
conn.close()