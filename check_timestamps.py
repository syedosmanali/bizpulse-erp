import sqlite3
from datetime import datetime

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row

print("=" * 80)
print("CHECKING BILL TIMESTAMPS")
print("=" * 80)

bills = conn.execute('SELECT id, bill_number, created_at FROM bills ORDER BY created_at DESC LIMIT 5').fetchall()
print('\nRecent Bills:')
for b in bills:
    print(f'Bill: {b["bill_number"]}, Created: {b["created_at"]}')

print("\n" + "=" * 80)
print("CHECKING SALES TIMESTAMPS")
print("=" * 80)

sales = conn.execute('SELECT bill_id, sale_date, sale_time, created_at FROM sales ORDER BY created_at DESC LIMIT 5').fetchall()
print('\nRecent Sales:')
for s in sales:
    print(f'Bill: {s["bill_id"]}, Date: {s["sale_date"]}, Time: {s["sale_time"]}, Created: {s["created_at"]}')

print("\n" + "=" * 80)
print("CURRENT SERVER TIME")
print("=" * 80)
print(f'Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

conn.close()
