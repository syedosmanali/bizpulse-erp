import sqlite3
import json
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

print("=== CURRENT DASHBOARD DATA ===")

# Check today's date
today = datetime.now().date()
print(f"Today's date: {today}")

# Check bills table for today
cursor.execute("""
    SELECT 
        COUNT(*) as total_bills,
        SUM(total_amount) as total_revenue,
        SUM(paid_amount) as total_paid
    FROM bills 
    WHERE DATE(created_at) = ?
""", (str(today),))

bill_stats = cursor.fetchone()
print(f"\nToday's Bills:")
print(f"  Total bills: {bill_stats[0]}")
print(f"  Total revenue: {bill_stats[1] or 0}")
print(f"  Total paid: {bill_stats[2] or 0}")

# Check payments table for today
cursor.execute("""
    SELECT 
        COUNT(*) as total_payments,
        SUM(amount) as total_payment_amount,
        COUNT(CASE WHEN payment_method = 'Cash' THEN 1 END) as cash_count,
        SUM(CASE WHEN payment_method = 'Cash' THEN amount ELSE 0 END) as cash_amount,
        COUNT(CASE WHEN payment_method = 'Credit' THEN 1 END) as credit_count,
        SUM(CASE WHEN payment_method = 'Credit' THEN amount ELSE 0 END) as credit_amount,
        COUNT(CASE WHEN payment_method = 'Cheque' THEN 1 END) as cheque_count,
        SUM(CASE WHEN payment_method = 'Cheque' THEN amount ELSE 0 END) as cheque_amount
    FROM payments 
    WHERE DATE(payment_date) = ?
""", (str(today),))

payment_stats = cursor.fetchone()
print(f"\nToday's Payments:")
print(f"  Total payments: {payment_stats[0]}")
print(f"  Total payment amount: {payment_stats[1] or 0}")
print(f"  Cash payments: {payment_stats[2]} (${payment_stats[3] or 0})")
print(f"  Credit payments: {payment_stats[4]} (${payment_stats[5] or 0})")
print(f"  Cheque payments: {payment_stats[6]} (${payment_stats[7] or 0})")

# Check revenue calculation logic
cursor.execute("""
    SELECT 
        b.id,
        b.total_amount,
        b.paid_amount,
        b.payment_status,
        p.amount as payment_amount,
        p.payment_method,
        p.payment_date
    FROM bills b
    LEFT JOIN payments p ON b.id = p.bill_id
    WHERE DATE(b.created_at) = ?
    ORDER BY b.id
""", (str(today),))

bills = cursor.fetchall()
print(f"\nDetailed Bills for Today:")
for bill in bills:
    print(f"  Bill {bill[0]}: ${bill[1]} total, ${bill[2]} paid, status: {bill[3]}")
    if bill[4]:
        print(f"    Payment: ${bill[4]} via {bill[5]} on {bill[6]}")

conn.close()