import sqlite3
from datetime import datetime

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row
today = datetime.now().strftime('%Y-%m-%d')
user_id = 'BIZPULSE-ADMIN-001'

print('=== CHECKING ALL DASHBOARD QUERIES ===')
print(f'User: {user_id}')
print(f'Today: {today}')
print()

print('1. Recent Sales Section (premium-sections):')
bills1 = conn.execute('''
    SELECT b.id, b.bill_number, b.created_at 
    FROM bills b 
    LEFT JOIN customers c ON b.customer_id = c.id 
    LEFT JOIN bill_items bi ON b.id = bi.bill_id 
    WHERE b.status = "completed" AND b.business_owner_id = ? 
    GROUP BY b.id 
    ORDER BY b.created_at DESC 
    LIMIT 5
''', (user_id,)).fetchall()
print(f'Count: {len(bills1)}')
for b in bills1:
    print(f'  {b["bill_number"]} - {b["created_at"]}')

print()
print('2. Activities/Sales Route:')
bills2 = conn.execute('''
    SELECT b.id, b.bill_number, b.created_at 
    FROM bills b 
    LEFT JOIN customers c ON b.customer_id = c.id 
    WHERE b.status = "completed" AND b.business_owner_id = ? 
    ORDER BY b.created_at DESC 
    LIMIT 5
''', (user_id,)).fetchall()
print(f'Count: {len(bills2)}')
for b in bills2:
    print(f'  {b["bill_number"]} - {b["created_at"]}')

print()
print('3. All Bills for User Today:')
bills3 = conn.execute('''
    SELECT b.id, b.bill_number, b.created_at 
    FROM bills b 
    WHERE DATE(b.created_at) = ? AND b.business_owner_id = ? 
    ORDER BY b.created_at DESC
''', (today, user_id)).fetchall()
print(f'Count: {len(bills3)}')
for b in bills3:
    print(f'  {b["bill_number"]} - {b["created_at"]}')

print()
print('4. All Bills for User (All Time):')
bills4 = conn.execute('''
    SELECT b.id, b.bill_number, b.created_at 
    FROM bills b 
    WHERE b.business_owner_id = ? 
    ORDER BY b.created_at DESC
''', (user_id,)).fetchall()
print(f'Count: {len(bills4)}')
for b in bills4:
    print(f'  {b["bill_number"]} - {b["created_at"]}')

conn.close()