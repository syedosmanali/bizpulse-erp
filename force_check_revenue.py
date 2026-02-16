"""
Force check what's in the database and what revenue should be
"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

today = datetime.now().strftime('%Y-%m-%d')

print("=" * 80)
print("FORCE CHECK - What's causing revenue to show?")
print("=" * 80)

# 1. Check all bills today
print("\n1. ALL BILLS TODAY:")
cursor.execute("""
    SELECT bill_number, total_amount, payment_method, payment_status
    FROM bills 
    WHERE DATE(created_at) = ?
""", (today,))

for row in cursor.fetchall():
    print(f"  {row['bill_number']}: ₹{row['total_amount']:.2f} | Method: {row['payment_method']} | Status: {row['payment_status']}")

# 2. Check all payments today
print("\n2. ALL PAYMENTS TODAY:")
cursor.execute("""
    SELECT p.amount, p.method, b.bill_number, b.payment_status
    FROM payments p
    JOIN bills b ON p.bill_id = b.id
    WHERE DATE(p.processed_at) = ?
""", (today,))

payments = cursor.fetchall()
if not payments:
    print("  NO PAYMENTS FOUND!")
else:
    for row in payments:
        status_flag = "❌ CHEQUE_DEPOSITED" if row['payment_status'] == 'cheque_deposited' else "✅ CLEARED"
        print(f"  {row['bill_number']}: ₹{row['amount']:.2f} | Method: {row['method']} | Status: {row['payment_status']} {status_flag}")

# 3. Calculate revenue WITH cheque_deposited
print("\n3. REVENUE CALCULATION:")
cursor.execute("""
    SELECT COALESCE(SUM(p.amount), 0) as revenue
    FROM payments p
    JOIN bills b ON p.bill_id = b.id
    WHERE DATE(p.processed_at) = ?
""", (today,))
with_cheques = cursor.fetchone()['revenue']
print(f"  WITH uncashed cheques: ₹{with_cheques:.2f}")

# 4. Calculate revenue WITHOUT cheque_deposited
cursor.execute("""
    SELECT COALESCE(SUM(p.amount), 0) as revenue
    FROM payments p
    JOIN bills b ON p.bill_id = b.id
    WHERE DATE(p.processed_at) = ?
    AND b.payment_status != 'cheque_deposited'
""", (today,))
without_cheques = cursor.fetchone()['revenue']
print(f"  WITHOUT uncashed cheques: ₹{without_cheques:.2f}")

print("\n" + "=" * 80)
print(f"EXPECTED DASHBOARD REVENUE: ₹{without_cheques:.2f}")
print(f"CURRENT DASHBOARD SHOWING: ₹3,288.66")
print("=" * 80)

# 5. Check if there are any non-cheque bills
print("\n4. NON-CHEQUE BILLS TODAY:")
cursor.execute("""
    SELECT bill_number, total_amount, payment_method, payment_status
    FROM bills 
    WHERE DATE(created_at) = ?
    AND payment_method != 'cheque'
""", (today,))

non_cheque = cursor.fetchall()
if not non_cheque:
    print("  NO NON-CHEQUE BILLS FOUND!")
else:
    for row in non_cheque:
        print(f"  {row['bill_number']}: ₹{row['total_amount']:.2f} | Method: {row['payment_method']} | Status: {row['payment_status']}")

conn.close()

print("\n⚠️  IF REVENUE SHOULD BE ₹0 BUT SHOWING ₹3,288.66:")
print("   → Server needs to be restarted to pick up code changes")
print("   → Run: START_SERVER.bat")
