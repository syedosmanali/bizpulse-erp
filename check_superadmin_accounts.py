"""
Check superadmin accounts
"""
from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Check clients table
cursor.execute("""
    SELECT id, company_name, contact_email, username, is_active, created_at
    FROM clients
    WHERE contact_email = 'bizpulse.erp@gmail.com'
    ORDER BY created_at
""")

accounts = cursor.fetchall()

print(f"\n📊 Total accounts with bizpulse.erp@gmail.com: {len(accounts)}")

if accounts:
    for i, acc in enumerate(accounts, 1):
        if isinstance(acc, dict):
            print(f"\n{i}. Company: {acc['company_name']}")
            print(f"   Username: {acc['username']}")
            print(f"   Email: {acc['contact_email']}")
            print(f"   Active: {acc['is_active']}")
            print(f"   Created: {acc['created_at']}")
        else:
            print(f"\n{i}. Company: {acc[1]}")
            print(f"   Username: {acc[3]}")
            print(f"   Email: {acc[2]}")
            print(f"   Active: {acc[4]}")
            print(f"   Created: {acc[5]}")

conn.close()
