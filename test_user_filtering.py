import sqlite3
from datetime import datetime

conn = sqlite3.connect('billing.db')
conn.row_factory = sqlite3.Row
today = datetime.now().strftime('%Y-%m-%d')

print(f'=== CHECKING USER FILTERING FOR TODAY ({today}) ===')

# Check all bills
all_bills = conn.execute('SELECT id, bill_number, business_owner_id, status, created_at FROM bills WHERE DATE(created_at) = ? ORDER BY created_at DESC', (today,)).fetchall()
print(f'\nAll bills today: {len(all_bills)}')
for i, b in enumerate(all_bills):
    print(f'{i+1}. {b["bill_number"]} - Owner: {b["business_owner_id"]} - Status: {b["status"]}')

# Check unique business owners
owners = conn.execute('SELECT DISTINCT business_owner_id FROM bills WHERE DATE(created_at) = ?', (today,)).fetchall()
print(f'\nUnique business owners: {len(owners)}')
for owner in owners:
    owner_id = owner["business_owner_id"]
    count = conn.execute('SELECT COUNT(*) as count FROM bills WHERE DATE(created_at) = ? AND business_owner_id = ?', (today, owner_id)).fetchone()
    print(f'Owner {owner_id}: {count["count"]} bills')

conn.close()