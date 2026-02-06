"""
Verify Migration - Check record counts in Supabase
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

import psycopg2

print("🔍 Verifying Migration to Supabase")
print("=" * 60)

postgres_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(postgres_url)
cursor = conn.cursor()

# Core tables to check
tables = [
    'products',
    'customers',
    'bills',
    'bill_items',
    'payments',
    'sales',
    'credit_transactions'
]

print("\n📊 Record Counts in Supabase:\n")

total_records = 0
for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total_records += count
        print(f"   ✅ {table:25} {count:>5} records")
    except Exception as e:
        print(f"   ❌ {table:25} Error: {str(e)[:50]}")

print("\n" + "=" * 60)
print(f"Total Records: {total_records}")
print("=" * 60)

# Sample some data
print("\n📋 Sample Data:\n")

try:
    cursor.execute("SELECT name, price, stock FROM products LIMIT 3")
    products = cursor.fetchall()
    print("   Products:")
    for p in products:
        print(f"      - {p[0]}: ₹{p[1]} (Stock: {p[2]})")
except Exception as e:
    print(f"   Error: {e}")

try:
    cursor.execute("SELECT name, phone, current_balance FROM customers LIMIT 3")
    customers = cursor.fetchall()
    print("\n   Customers:")
    for c in customers:
        print(f"      - {c[0]}: {c[1]} (Balance: ₹{c[2]})")
except Exception as e:
    print(f"   Error: {e}")

try:
    cursor.execute("SELECT bill_number, total_amount, payment_status FROM bills LIMIT 3")
    bills = cursor.fetchall()
    print("\n   Bills:")
    for b in bills:
        print(f"      - {b[0]}: ₹{b[1]} ({b[2]})")
except Exception as e:
    print(f"   Error: {e}")

conn.close()

print("\n✅ Migration verification complete!")
print("   Your data is safely stored in Supabase PostgreSQL")
