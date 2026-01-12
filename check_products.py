import sqlite3

conn = sqlite3.connect('billing.db')
c = conn.cursor()

# Check products by user_id
c.execute('SELECT user_id, COUNT(*) as cnt FROM products WHERE is_active=1 GROUP BY user_id ORDER BY cnt DESC LIMIT 10')
rows = c.fetchall()

print('Products by user_id:')
print('=' * 60)
for r in rows:
    user_id = r[0][:40] if r[0] else 'NULL'
    count = r[1]
    print(f'{user_id:40} : {count} products')

print('\n' + '=' * 60)
print(f'Total products: {sum([r[1] for r in rows])}')

# Check clients
print('\n' + '=' * 60)
print('Clients:')
c.execute('SELECT id, username, company_name FROM clients WHERE is_active=1 LIMIT 10')
clients = c.fetchall()
for client in clients:
    print(f'{client[1]:20} ({client[2]:30}) - ID: {client[0][:20]}...')

conn.close()
