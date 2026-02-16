"""
Check current database state to understand what's showing in dashboard
"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

today = datetime.now().strftime('%Y-%m-%d')

print("=" * 80)
print(f"Checking Database State for {today}")
print("=" * 80)

# Check today's bills
print("\n1. TODAY'S BILLS:")
cursor.execute("""
    SELECT bill_number, total_amount, payment_method, payment_status, is_credit, credit_balance
    FROM bills 
    WHERE DATE(created_at) = ?
    ORDER BY created_at DESC
""", (today,))

bills = cursor.fetchall()
print(f"Found {len(bills)} bills today\n")

for bill in bills:
    print(f"Bill: {bill['bill_number']}")
    print(f"  Amount: ₹{bill['total_amount']:.2f}")
    print(f"  Method: {bill['payment_method']}")
    print(f"  Status: {bill['payment_status']}")
    print(f"  Is Credit: {bill['is_credit']}")
    print(f"  Balance: ₹{bill['credit_balance']:.2f}")
    print()

# Check today's payments
print("\n2. TODAY'S PAYMENTS:")
cursor.execute("""
    SELECT p.id, p.bill_id, p.amount, p.method, p.processed_at, b.payment_status, b.bill_number
    FROM payments p
    JOIN bills b ON p.bill_id = b.id
    WHERE DATE(p.processed_at) = ?
    ORDER BY p.processed_at DESC
""", (today,))

payments = cursor.fetchall()
print(f"Found {len(payments)} payments today\n")

total_payment_amount = 0
for payment in payments:
    print(f"Payment ID: {payment['id']}")
    print(f"  Bill: {payment['bill_number']}")
    print(f"  Amount: ₹{payment['amount']:.2f}")
    print(f"  Method: {payment['method']}")
    print(f"  Bill Status: {payment['payment_status']}")
    print(f"  Processed: {payment['processed_at']}")
    total_payment_amount += payment['amount']
    print()

print(f"Total Payment Amount: ₹{total_payment_amount:.2f}")

# Check what revenue SHOULD be (excluding cheque_deposited)
print("\n3. CORRECT REVENUE CALCULATION:")
cursor.execute("""
    SELECT COALESCE(SUM(p.amount), 0) as revenue
    FROM payments p
    JOIN bills b ON p.bill_id = b.id
    WHERE DATE(p.processed_at) = ?
    AND b.payment_status != 'cheque_deposited'
""", (today,))

correct_revenue = cursor.fetchone()['revenue']
print(f"Revenue (excluding uncashed cheques): ₹{correct_revenue:.2f}")

# Check what revenue is CURRENTLY being calculated (including cheque_deposited)
cursor.execute("""
    SELECT COALESCE(SUM(p.amount), 0) as revenue
    FROM payments p
    JOIN bills b ON p.bill_id = b.id
    WHERE DATE(p.processed_at) = ?
""", (today,))

current_revenue = cursor.fetchone()['revenue']
print(f"Revenue (including uncashed cheques): ₹{current_revenue:.2f}")

print("\n" + "=" * 80)
print("ANALYSIS:")
print(f"Difference: ₹{current_revenue - correct_revenue:.2f}")
print("This difference should be from cheque_deposited bills")
print("=" * 80)

conn.close()
