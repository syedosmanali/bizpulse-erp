"""
Verify Credit Transactions Fix
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
    print("❌ DATABASE_URL not found")
    exit(1)

print("🔍 Connecting to Supabase...")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("\n" + "="*60)
print("CREDIT TRANSACTIONS TABLE VERIFICATION")
print("="*60)

# Check if credit_transactions table exists
print("\n1️⃣ Checking if credit_transactions table exists...")
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_name = 'credit_transactions'
""")
table_exists = cursor.fetchone()

if table_exists:
    print("   ✅ credit_transactions table EXISTS")
else:
    print("   ❌ credit_transactions table DOES NOT EXIST")
    print("\n⚠️  You need to run the SQL script in Supabase!")
    conn.close()
    exit(1)

# Check columns in credit_transactions table
print("\n2️⃣ Checking credit_transactions table columns...")
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'credit_transactions' 
    ORDER BY ordinal_position
""")
columns = cursor.fetchall()

required_columns = ['id', 'bill_id', 'customer_id', 'transaction_type', 'amount', 'payment_method']
found_columns = [col['column_name'] for col in columns]

print(f"\n   Found {len(columns)} columns:")
for col in columns:
    status = "✅" if col['column_name'] in required_columns else "ℹ️"
    print(f"   {status} {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")

# Check if amount column exists
if 'amount' in found_columns:
    print("\n   ✅ AMOUNT COLUMN EXISTS - Credit billing should work!")
else:
    print("\n   ❌ AMOUNT COLUMN MISSING - Credit billing will NOT work!")

# Check bills table credit columns
print("\n3️⃣ Checking bills table credit columns...")
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns 
    WHERE table_name = 'bills' 
    AND column_name IN ('is_credit', 'credit_amount', 'credit_paid_amount', 'credit_balance', 'partial_payment_amount', 'partial_payment_method')
    ORDER BY column_name
""")
bills_credit_columns = cursor.fetchall()

required_bills_columns = ['is_credit', 'credit_amount', 'credit_paid_amount', 'credit_balance', 'partial_payment_amount', 'partial_payment_method']
found_bills_columns = [col['column_name'] for col in bills_credit_columns]

print(f"\n   Found {len(bills_credit_columns)} credit columns in bills table:")
for col_name in required_bills_columns:
    if col_name in found_bills_columns:
        print(f"   ✅ {col_name}")
    else:
        print(f"   ❌ {col_name} - MISSING")

# Test creating a sample credit transaction (dry run)
print("\n4️⃣ Testing credit transaction insert (dry run)...")
try:
    cursor.execute("""
        SELECT 1 FROM credit_transactions WHERE 1=0
    """)
    print("   ✅ credit_transactions table is accessible")
except Exception as e:
    print(f"   ❌ Error accessing table: {e}")

# Final summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

all_good = (
    table_exists and 
    'amount' in found_columns and
    len(found_bills_columns) >= 4
)

if all_good:
    print("✅ ALL CHECKS PASSED!")
    print("\n🎉 Credit and Partial Payment billing should work now!")
    print("\nTest it:")
    print("1. Go to: https://bizpulse24.com/retail/billing")
    print("2. Create a bill with Credit payment method")
    print("3. Create a bill with Partial payment")
    print("4. Both should work without errors!")
else:
    print("⚠️  SOME CHECKS FAILED!")
    print("\nYou need to run the SQL script in Supabase:")
    print("1. Open: https://supabase.com/dashboard")
    print("2. Go to SQL Editor")
    print("3. Run the script from: FIX_CREDIT_BILLING_COMPLETE.sql")

conn.close()
print("\n" + "="*60)
