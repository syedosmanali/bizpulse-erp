import sqlite3

# Check database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Check clients table
cursor.execute("SELECT COUNT(*) FROM clients")
count = cursor.fetchone()[0]
print(f"Total clients: {count}")

if count > 0:
    cursor.execute("SELECT id, company_name, contact_name, contact_email FROM clients LIMIT 3")
    clients = cursor.fetchall()
    for client in clients:
        print(f"ID: {client[0]}, Company: {client[1]}, Name: {client[2]}, Email: {client[3]}")

conn.close()