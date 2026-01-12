import sqlite3
from datetime import datetime

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row
user_id = 'BIZPULSE-ADMIN-001'
today = datetime.now().strftime('%Y-%m-%d')

print('=== TESTING TODAY FILTER FIX ===')
print(f'User: {user_id}')
print(f'Today: {today}')
print()

# Test the NEW query (with today filter)
print('NEW Query (with today filter):')
new_query = '''
    SELECT b.id, b.bill_number, b.business_owner_id, b.created_at
    FROM bills b
    LEFT JOIN customers c ON b.customer_id = c.id
    WHERE b.status = 'completed' AND DATE(b.created_at) = ?
    AND b.business_owner_id = ?
    ORDER BY b.created_at DESC LIMIT 8
'''
new_bills = conn.execute(new_query, (today, user_id)).fetchall()
print(f'Count: {len(new_bills)}')
for b in new_bills:
    print(f'  {b["bill_number"]} - {b["created_at"]}')

print()
if len(new_bills) == 5:
    print('✅ FIXED! Now shows 5 bills (same as sales module)')
else:
    print(f'❌ Still showing {len(new_bills)} bills instead of 5')

conn.close()