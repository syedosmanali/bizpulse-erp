"""
Check bills data and business_owner_id
"""
from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Check total bills
cursor.execute('SELECT COUNT(*) as count FROM bills')
result = cursor.fetchone()
total_bills = result['count'] if isinstance(result, dict) else result[0]
print(f"📊 Total bills in database: {total_bills}")

# Check bills with business_owner_id
cursor.execute('SELECT COUNT(*) as count FROM bills WHERE business_owner_id IS NOT NULL')
result = cursor.fetchone()
bills_with_owner = result['count'] if isinstance(result, dict) else result[0]
print(f"✅ Bills with business_owner_id: {bills_with_owner}")

# Check bills without business_owner_id
cursor.execute('SELECT COUNT(*) as count FROM bills WHERE business_owner_id IS NULL')
result = cursor.fetchone()
bills_without_owner = result['count'] if isinstance(result, dict) else result[0]
print(f"❌ Bills without business_owner_id: {bills_without_owner}")

# Show sample bills
print("\n📋 Sample bills:")
cursor.execute('SELECT id, bill_number, business_owner_id, customer_name, total_amount FROM bills LIMIT 5')
bills = cursor.fetchall()

for bill in bills:
    bill_dict = dict(bill)
    print(f"  - Bill: {bill_dict.get('bill_number')}, Owner ID: {bill_dict.get('business_owner_id')}, Customer: {bill_dict.get('customer_name')}, Amount: {bill_dict.get('total_amount')}")

# Check current user session
print("\n👤 To fix this, we need to know your user_id from the session")
print("   The invoice module filters bills by business_owner_id matching your user_id")

conn.close()
