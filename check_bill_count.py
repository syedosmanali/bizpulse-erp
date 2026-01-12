import sqlite3
from datetime import datetime

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row
today = datetime.now().strftime('%Y-%m-%d')

print(f'=== BILLS FOR TODAY ({today}) ===')
bills = conn.execute('SELECT id, bill_number, status, created_at FROM bills WHERE DATE(created_at) = ? ORDER BY created_at DESC', (today,)).fetchall()
print(f'Total bills in database: {len(bills)}')
for i, b in enumerate(bills):
    print(f'{i+1}. {b["bill_number"]} - Status: {b["status"]} - Time: {b["created_at"]}')

print(f'\n=== SALES ENTRIES FOR TODAY ===')
sales = conn.execute('SELECT DISTINCT bill_id, bill_number FROM sales WHERE DATE(created_at) = ?', (today,)).fetchall()
print(f'Total unique sales entries: {len(sales)}')

print(f'\n=== DASHBOARD QUERY (completed only) ===')
dashboard_bills = conn.execute('SELECT id, bill_number, status, created_at FROM bills WHERE DATE(created_at) = ? AND status = "completed" ORDER BY created_at DESC', (today,)).fetchall()
print(f'Dashboard shows: {len(dashboard_bills)} bills')
for i, b in enumerate(dashboard_bills):
    print(f'{i+1}. {b["bill_number"]} - Status: {b["status"]}')

print(f'\n=== SALES MODULE QUERY (all bills) ===')
sales_module_bills = conn.execute('SELECT DISTINCT s.bill_id, s.bill_number, b.status FROM sales s LEFT JOIN bills b ON s.bill_id = b.id WHERE DATE(s.created_at) = ? ORDER BY s.created_at DESC', (today,)).fetchall()
print(f'Sales module shows: {len(sales_module_bills)} bills')
for i, b in enumerate(sales_module_bills):
    print(f'{i+1}. {b["bill_number"]} - Status: {b["status"]}')

conn.close()