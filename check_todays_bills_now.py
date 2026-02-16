"""
Check today's bills and their business_owner_id
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    exit(1)

print("🔍 Connecting to Supabase...")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor(cursor_factory=RealDictCursor)

today = datetime.now().strftime('%Y-%m-%d')
print(f"\n📅 Checking bills for: {today}")

# Get all bills from today
cursor.execute("""
    SELECT 
        id, 
        bill_number, 
        customer_name, 
        total_amount, 
        payment_method,
        business_owner_id,
        user_id,
        created_at
    FROM bills
    WHERE created_at::date = %s
    ORDER BY created_at DESC
""", (today,))

bills = cursor.fetchall()

print(f"\n📊 Found {len(bills)} bills today:")
print("="*80)

if bills:
    for bill in bills:
        print(f"\n📄 Bill: {bill['bill_number']}")
        print(f"   Customer: {bill['customer_name'] or 'Walk-in'}")
        print(f"   Amount: ₹{bill['total_amount']}")
        print(f"   Payment: {bill['payment_method']}")
        print(f"   business_owner_id: {bill['business_owner_id'] or 'NULL ⚠️'}")
        print(f"   user_id: {bill['user_id'] or 'NULL ⚠️'}")
        print(f"   Created: {bill['created_at']}")
else:
    print("\n⚠️  NO BILLS FOUND FOR TODAY!")
    print("\nLet me check all bills in the database...")
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN business_owner_id IS NULL THEN 1 END) as null_owner,
            COUNT(CASE WHEN business_owner_id IS NOT NULL THEN 1 END) as has_owner
        FROM bills
    """)
    
    stats = cursor.fetchone()
    print(f"\n📊 Total bills in database: {stats['total']}")
    print(f"   - With business_owner_id: {stats['has_owner']}")
    print(f"   - Without business_owner_id (NULL): {stats['null_owner']}")
    
    # Get most recent bills
    cursor.execute("""
        SELECT 
            bill_number,
            customer_name,
            total_amount,
            business_owner_id,
            created_at
        FROM bills
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    recent = cursor.fetchall()
    print(f"\n📋 Last 5 bills in database:")
    for bill in recent:
        print(f"   {bill['bill_number']} - {bill['customer_name']} - ₹{bill['total_amount']} - {bill['created_at']}")

# Check clients
print("\n\n👥 Checking clients in database:")
cursor.execute("SELECT id, company_name, username FROM clients ORDER BY created_at DESC LIMIT 5")
clients = cursor.fetchall()

if clients:
    print(f"Found {len(clients)} clients:")
    for client in clients:
        print(f"   - {client['company_name']} (ID: {client['id']}, Username: {client['username']})")
else:
    print("⚠️  NO CLIENTS FOUND!")

conn.close()

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Today's date: {today}")
print(f"Bills today: {len(bills)}")
print("\nIf bills are missing, they might be:")
print("1. Filtered by business_owner_id (check session)")
print("2. Created with wrong date")
print("3. Not committed to database")
print("="*80)
