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
        SUM(total_amount) as total_revenue
    FROM bills 
    WHERE DATE(created_at) = ?
""", (str(today),))

bill_stats = cursor.fetchone()
print(f"\nToday's Bills:")
print(f"  Total bills: {bill_stats[0]}")
print(f"  Total revenue: {bill_stats[1] or 0}")

# Check payments table for today
cursor.execute("""
    SELECT 
        COUNT(*) as total_payments,
        SUM(amount) as total_payment_amount,
        COUNT(CASE WHEN method = 'Cash' THEN 1 END) as cash_count,
        SUM(CASE WHEN method = 'Cash' THEN amount ELSE 0 END) as cash_amount,
        COUNT(CASE WHEN method = 'Credit' THEN 1 END) as credit_count,
        SUM(CASE WHEN method = 'Credit' THEN amount ELSE 0 END) as credit_amount,
        COUNT(CASE WHEN method = 'Cheque' THEN 1 END) as cheque_count,
        SUM(CASE WHEN method = 'Cheque' THEN amount ELSE 0 END) as cheque_amount
    FROM payments 
    WHERE DATE(processed_at) = ?
""", (str(today),))

payment_stats = cursor.fetchone()
print(f"\nToday's Payments:")
print(f"  Total payments: {payment_stats[0]}")
print(f"  Total payment amount: {payment_stats[1] or 0}")
print(f"  Cash payments: {payment_stats[2]} (${payment_stats[3] or 0})")
print(f"  Credit payments: {payment_stats[4]} (${payment_stats[5] or 0})")
print(f"  Cheque payments: {payment_stats[6]} (${payment_stats[7] or 0})")

# Check revenue calculation - should only count cash payments
cash_revenue = payment_stats[3] or 0
print(f"\n=== REVENUE CALCULATION ===")
print(f"Cash Revenue (should be shown in dashboard): ${cash_revenue}")

# Net profit calculation
net_profit = cash_revenue  # Simplified - assuming no expenses tracked
print(f"Net Profit (should be shown in dashboard): ${net_profit}")

conn.close()