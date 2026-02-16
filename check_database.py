import sys
sys.path.append('.')

from modules.shared.database import get_db_connection, get_db_type
from datetime import datetime

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')
print(f"Today's date: {today}")

# Get database connection
conn = get_db_connection()
cursor = conn.cursor()
db_type = get_db_type()

print(f"Database type: {db_type}")

# Check payments table
if db_type == 'postgresql':
    cursor.execute("SELECT COUNT(*) as count FROM payments")
else:
    cursor.execute("SELECT COUNT(*) as count FROM payments")

payment_count = cursor.fetchone()
print(f"Total payments in database: {payment_count['count'] if payment_count else 0}")

# Check today's payments
if db_type == 'postgresql':
    cursor.execute("SELECT id, bill_id, method, amount, processed_at FROM payments WHERE CAST(processed_at AS DATE) = %s", [today])
else:
    cursor.execute("SELECT id, bill_id, method, amount, processed_at FROM payments WHERE DATE(processed_at) = ?", [today])

today_payments = cursor.fetchall()
print(f"\nToday's payments ({len(today_payments)}):")
for payment in today_payments:
    print(f"  - ID: {payment['id']}")
    print(f"    Bill ID: {payment['bill_id']}")
    print(f"    Method: {payment['method']}")
    print(f"    Amount: {payment['amount']}")
    print(f"    Processed: {payment['processed_at']}")
    print()

# Check bills from today
if db_type == 'postgresql':
    cursor.execute("SELECT bill_number, total_amount, payment_method, created_at FROM bills WHERE CAST(created_at AS DATE) = %s", [today])
else:
    cursor.execute("SELECT bill_number, total_amount, payment_method, created_at FROM bills WHERE DATE(created_at) = ?", [today])

today_bills = cursor.fetchall()
print(f"\nToday's bills ({len(today_bills)}):")
for bill in today_bills:
    print(f"  - {bill['bill_number']}: ₹{bill['total_amount']} ({bill['payment_method']}) created at {bill['created_at']}")

conn.close()