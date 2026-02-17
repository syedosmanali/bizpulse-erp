"""
Check all bills in database
"""
from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Total bills
cursor.execute("SELECT COUNT(*) FROM bills")
result = cursor.fetchone()
total = result['count'] if isinstance(result, dict) else result[0]

print(f"\n📊 Total Bills: {total}")

# Bills by client
cursor.execute("""
    SELECT business_owner_id, COUNT(*) as count
    FROM bills
    WHERE business_owner_id IS NOT NULL
    GROUP BY business_owner_id
    ORDER BY count DESC
    LIMIT 10
""")

bills_by_client = cursor.fetchall()

if bills_by_client:
    print("\n📋 Bills by Client:")
    for row in bills_by_client:
        if isinstance(row, dict):
            client_id = row['business_owner_id']
            count = row['count']
        else:
            client_id = row[0]
            count = row[1]
        
        # Get client name
        cursor.execute("SELECT company_name FROM clients WHERE id = %s", (client_id,))
        client = cursor.fetchone()
        client_name = client['company_name'] if client and isinstance(client, dict) else (client[0] if client else 'Unknown')
        
        print(f"   {client_name}: {count} bills")

# Recent bills
print("\n🕐 Recent 5 Bills:")
cursor.execute("""
    SELECT bill_number, customer_name, total_amount, business_owner_id, created_at
    FROM bills
    ORDER BY created_at DESC
    LIMIT 5
""")

recent = cursor.fetchall()
for bill in recent:
    if isinstance(bill, dict):
        print(f"\n   {bill['bill_number']}")
        print(f"   Customer: {bill['customer_name']}")
        print(f"   Amount: ₹{bill['total_amount']}")
        print(f"   Date: {bill['created_at']}")
    else:
        print(f"\n   {bill[0]}")
        print(f"   Customer: {bill[1]}")
        print(f"   Amount: ₹{bill[2]}")
        print(f"   Date: {bill[4]}")

conn.close()
