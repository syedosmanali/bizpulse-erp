import sqlite3
from datetime import datetime

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

today = datetime.now().strftime('%Y-%m-%d')

print("=" * 60)
print("DATA CHECK - Current Status")
print("=" * 60)

# Invoices
cursor.execute('SELECT COUNT(*) FROM invoices')
total_invoices = cursor.fetchone()[0]
print(f"\n1. Total Invoices: {total_invoices}")

if total_invoices > 0:
    cursor.execute('SELECT invoice_number, total_amount, invoice_date FROM invoices ORDER BY created_at DESC LIMIT 3')
    print("   Recent invoices:")
    for row in cursor.fetchall():
        print(f"   - {row[0]}: ₹{row[1]} ({row[2]})")

# Bills
cursor.execute('SELECT COUNT(*) FROM bills WHERE DATE(created_at) = ?', (today,))
today_bills = cursor.fetchone()[0]
print(f"\n2. Today's Bills: {today_bills}")

if today_bills > 0:
    cursor.execute('SELECT bill_number, total_amount, created_at FROM bills WHERE DATE(created_at) = ? ORDER BY created_at DESC LIMIT 3', (today,))
    print("   Recent bills:")
    for row in cursor.fetchall():
        print(f"   - {row[0]}: ₹{row[1]} ({row[2]})")

# Sales
cursor.execute('SELECT COUNT(*) FROM sales WHERE sale_date = ?', (today,))
today_sales = cursor.fetchone()[0]
print(f"\n3. Today's Sales Records: {today_sales}")

if today_sales > 0:
    cursor.execute('SELECT bill_number, product_name, quantity, total_price FROM sales WHERE sale_date = ? ORDER BY created_at DESC LIMIT 3', (today,))
    print("   Recent sales:")
    for row in cursor.fetchall():
        print(f"   - {row[0]}: {row[1]} x{row[2]} = ₹{row[3]}")

conn.close()

print("\n" + "=" * 60)
print("✅ Data check complete!")
print("=" * 60)
