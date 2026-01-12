import sqlite3
from datetime import datetime

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row
user_id = 'BIZPULSE-ADMIN-001'

print('=== TESTING RETAIL ACTIVITY FIX ===')
print(f'User: {user_id}')
print()

# Test the OLD query (with IS NULL)
print('OLD Query (with IS NULL):')
old_query = '''
    SELECT b.id, b.bill_number, b.business_owner_id, b.created_at
    FROM bills b
    LEFT JOIN customers c ON b.customer_id = c.id
    WHERE b.status = 'completed'
    AND (b.business_owner_id = ? OR b.business_owner_id IS NULL)
    ORDER BY b.created_at DESC LIMIT 8
'''
old_bills = conn.execute(old_query, (user_id,)).fetchall()
print(f'Count: {len(old_bills)}')
for b in old_bills:
    print(f'  {b["bill_number"]} - Owner: {b["business_owner_id"]}')

print()

# Test the NEW query (without IS NULL)
print('NEW Query (without IS NULL):')
new_query = '''
    SELECT b.id, b.bill_number, b.business_owner_id, b.created_at
    FROM bills b
    LEFT JOIN customers c ON b.customer_id = c.id
    WHERE b.status = 'completed'
    AND b.business_owner_id = ?
    ORDER BY b.created_at DESC LIMIT 8
'''
new_bills = conn.execute(new_query, (user_id,)).fetchall()
print(f'Count: {len(new_bills)}')
for b in new_bills:
    print(f'  {b["bill_number"]} - Owner: {b["business_owner_id"]}')

print()
if len(new_bills) == 5:
    print('✅ FIXED! Now shows 5 bills (same as sales module)')
else:
    print(f'❌ Still showing {len(new_bills)} bills')

conn.close()