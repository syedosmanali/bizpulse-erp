import sqlite3

# Connect to database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Try different date formats to find today's bills
print("Searching for today's bills with different date formats...")

# Check various date patterns
patterns = [
    '2026-02-10%',
    '%2026-02-10%',
    '2026-02-10',
    '%-02-10%',
    '%10T%',
    '%10 %'
]

for pattern in patterns:
    cursor.execute("SELECT bill_number, total_amount, created_at FROM bills WHERE created_at LIKE ?", (pattern,))
    bills = cursor.fetchall()
    if bills:
        print(f"\nFound bills matching pattern '{pattern}':")
        for bill in bills:
            print(f"  {bill[0]}: ₹{bill[1]} - {bill[2]}")

# Also check exact date comparison
print("\nChecking with DATE() function:")
cursor.execute("SELECT bill_number, total_amount, created_at FROM bills WHERE DATE(created_at) = '2026-02-10'")
bills = cursor.fetchall()
if bills:
    print("Found bills with DATE() = '2026-02-10':")
    for bill in bills:
        print(f"  {bill[0]}: ₹{bill[1]} - {bill[2]}")

conn.close()