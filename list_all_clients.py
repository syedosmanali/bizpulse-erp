"""
List all clients in database
"""
from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT id, company_name, contact_email, username, is_active, created_at
    FROM clients
    ORDER BY created_at DESC
""")

clients = cursor.fetchall()

print(f"\n📊 Total Clients: {len(clients)}\n")

for i, client in enumerate(clients, 1):
    if isinstance(client, dict):
        print(f"{i}. ID: {client['id']}")
        print(f"   Company: {client['company_name']}")
        print(f"   Email: {client['contact_email']}")
        print(f"   Username: {client['username']}")
        print(f"   Active: {client['is_active']}")
        print(f"   Created: {client['created_at']}\n")
    else:
        print(f"{i}. ID: {client[0]}")
        print(f"   Company: {client[1]}")
        print(f"   Email: {client[2]}")
        print(f"   Username: {client[3]}")
        print(f"   Active: {client[4]}")
        print(f"   Created: {client[5]}\n")

conn.close()
