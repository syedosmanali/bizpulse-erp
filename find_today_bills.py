import sqlite3

# Connect to database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Check for any bills containing today's date
print("Checking for bills with today's date...")
cursor.execute("SELECT bill_number, total_amount, created_at FROM bills WHERE created_at LIKE '%2026-02-10%'")
bills = cursor.fetchall()

if bills:
    print("Found bills from today:")
    for bill in bills:
        print(f"  {bill[0]}: ₹{bill[1]} - {bill[2]}")
    
    # Delete them
    cursor.execute("DELETE FROM bills WHERE created_at LIKE '%2026-02-10%'")
    deleted = cursor.rowcount
    print(f"\nDeleted {deleted} bills from today")
    conn.commit()
else:
    print("No bills found from today")

conn.close()