"""
Check Ali's account details
"""
from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Get Ali's client info
cursor.execute("SELECT id, company_name, contact_email, username FROM clients WHERE company_name LIKE %s", ('%Ali%',))
client = cursor.fetchone()

if client:
    if isinstance(client, dict):
        client_id = client['id']
        company = client['company_name']
        email = client['contact_email']
        username = client['username']
    else:
        client_id = client[0]
        company = client[1]
        email = client[2]
        username = client[3]
    
    print(f"\n👤 Client: {company}")
    print(f"   Email: {email}")
    print(f"   Username: {username}")
    print(f"   ID: {client_id}")
    
    # Get bills
    cursor.execute("SELECT COUNT(*) FROM bills WHERE business_owner_id = %s", (client_id,))
    result = cursor.fetchone()
    count = result['count'] if isinstance(result, dict) else result[0]
    
    print(f"\n📊 Total Bills: {count}")
    
    # Get bill details
    cursor.execute("""
        SELECT bill_number, customer_name, total_amount, payment_method, created_at
        FROM bills
        WHERE business_owner_id = %s
        ORDER BY created_at DESC
    """, (client_id,))
    
    bills = cursor.fetchall()
    
    if bills:
        print(f"\n📋 Bill Details:")
        for bill in bills:
            if isinstance(bill, dict):
                print(f"\n   {bill['bill_number']}")
                print(f"   Customer: {bill['customer_name']}")
                print(f"   Amount: ₹{bill['total_amount']}")
                print(f"   Payment: {bill['payment_method']}")
                print(f"   Date: {bill['created_at']}")
            else:
                print(f"\n   {bill[0]}")
                print(f"   Customer: {bill[1]}")
                print(f"   Amount: ₹{bill[2]}")
                print(f"   Payment: {bill[3]}")
                print(f"   Date: {bill[4]}")
else:
    print("❌ Ali's account not found")

conn.close()
