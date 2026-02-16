"""
Check bills in local Supabase connection
"""
from modules.shared.database import get_db_connection, get_db_type
from datetime import datetime

print("="*60)
print("CHECKING BILLS IN LOCAL DATABASE")
print("="*60)

db_type = get_db_type()
print(f"\n📊 Database Type: {db_type}")

conn = get_db_connection()
cursor = conn.cursor()

# Get total bills
cursor.execute("SELECT COUNT(*) FROM bills")
result = cursor.fetchone()
total = result['count'] if isinstance(result, dict) else result[0]
print(f"\n📋 Total Bills: {total}")

# Get recent bills
print(f"\n🔍 Recent 10 Bills:")
cursor.execute("""
    SELECT bill_number, customer_name, total_amount, payment_method, created_at
    FROM bills
    ORDER BY created_at DESC
    LIMIT 10
""")

bills = cursor.fetchall()

if bills:
    for bill in bills:
        if isinstance(bill, dict):
            print(f"\n   Bill: {bill['bill_number']}")
            print(f"   Customer: {bill['customer_name'] or 'Walk-in'}")
            print(f"   Amount: ₹{bill['total_amount']}")
            print(f"   Payment: {bill['payment_method']}")
            print(f"   Date: {bill['created_at']}")
        else:
            print(f"\n   Bill: {bill[0]}")
            print(f"   Customer: {bill[1] or 'Walk-in'}")
            print(f"   Amount: ₹{bill[2]}")
            print(f"   Payment: {bill[3]}")
            print(f"   Date: {bill[4]}")
else:
    print("   No bills found!")

# Get today's bills
today = datetime.now().strftime('%Y-%m-%d')
cursor.execute(f"""
    SELECT COUNT(*) FROM bills
    WHERE DATE(created_at) = '{today}'
""")
result = cursor.fetchone()
today_count = result['count'] if isinstance(result, dict) else result[0]
print(f"\n📅 Today's Bills: {today_count}")

conn.close()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"✅ Connected to: {db_type.upper()}")
print(f"✅ Total Bills: {total}")
print(f"✅ Today's Bills: {today_count}")
print("\nIf you created a bill on .com, it should appear here!")
print("="*60)
