"""
Verify Supabase Fix - Check if all columns and tables exist
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    exit(1)

print("🔍 Connecting to Supabase database...")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("\n" + "="*60)
print("VERIFICATION REPORT")
print("="*60)

# Check bills table columns
print("\n1️⃣ Checking bills table columns...")
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'bills' 
    AND column_name IN ('customer_phone', 'business_owner_id', 'user_id', 'paid_amount')
    ORDER BY column_name
""")
bills_columns = [row['column_name'] for row in cursor.fetchall()]

required_bills_columns = ['business_owner_id', 'customer_phone', 'paid_amount', 'user_id']
for col in required_bills_columns:
    if col in bills_columns:
        print(f"   ✅ {col} - EXISTS")
    else:
        print(f"   ❌ {col} - MISSING")

# Check user management tables
print("\n2️⃣ Checking user management tables...")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_name IN ('user_roles', 'user_accounts', 'user_activity_log', 'user_sessions')
    ORDER BY table_name
""")
user_tables = [row['table_name'] for row in cursor.fetchall()]

required_tables = ['user_accounts', 'user_activity_log', 'user_roles', 'user_sessions']
for table in required_tables:
    if table in user_tables:
        print(f"   ✅ {table} - EXISTS")
    else:
        print(f"   ❌ {table} - MISSING")

# Check other tables
print("\n3️⃣ Checking other tables for business_owner_id...")
tables_to_check = ['products', 'customers', 'sales']
for table in tables_to_check:
    cursor.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table}' AND column_name = 'business_owner_id'
    """)
    result = cursor.fetchone()
    if result:
        print(f"   ✅ {table}.business_owner_id - EXISTS")
    else:
        print(f"   ❌ {table}.business_owner_id - MISSING")

# Check indexes
print("\n4️⃣ Checking indexes...")
cursor.execute("""
    SELECT indexname 
    FROM pg_indexes 
    WHERE indexname LIKE 'idx_bills%' OR indexname LIKE 'idx_user%'
    ORDER BY indexname
    LIMIT 5
""")
indexes = cursor.fetchall()
if indexes:
    print(f"   ✅ Found {len(indexes)} indexes")
    for idx in indexes:
        print(f"      - {idx['indexname']}")
else:
    print("   ⚠️  No indexes found (may still be creating)")

# Final summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

all_bills_cols = all(col in bills_columns for col in required_bills_columns)
all_user_tables = all(table in user_tables for table in required_tables)

if all_bills_cols and all_user_tables:
    print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
    print("\n🎉 You can now:")
    print("   1. Create bills at: https://bizpulse24.com/retail/billing")
    print("   2. Manage users at: https://bizpulse24.com/user-management")
    print("   3. View dashboard at: https://bizpulse24.com/retail/dashboard")
else:
    print("⚠️  Some fixes are missing. Please run the SQL script again.")

cursor.close()
conn.close()

print("\n" + "="*60)
